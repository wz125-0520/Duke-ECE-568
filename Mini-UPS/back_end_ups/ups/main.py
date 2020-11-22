import psycopg2
import socket
import world_ups_pb2, amazon_ups_pb2
import sys
import threading
import select
from basic import *
#from handle_amazon import *
#from handle_world import *
import smtplib
from email.mime.text import MIMEText
import time

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

seq = 0
lock = threading.Lock()
setlock = threading.Lock()
amazon_socket = None
world_socket = None
ack_set = set()
worldid = 0

#===============================================================
# Handle World

def send_email(package_id):
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("select owner from ups_package where packageid='" + str(package_id) + "'")
    packages = cur.fetchall()
    username = packages[0][0]

    cur.execute("select email from auth_user where username='" + username + "'")
    emails = cur.fetchall()

    if len(emails) != 0:
        email = emails[0][0]

        mail_host = 'smtp.gmail.com'  
        mail_user = 'WeihanYq'  
        mail_pass = 'Zwh_970520'   
        sender = 'WeihanYq@gmail.com'  
        receivers = [email]

        context = "Dear " + username + ":\n\nYour package " + str(package_id) + " has arrived, please check it!\n"\
                    + "Hope to see you next time!\n\nUPS service center"

        message = MIMEText(context, 'plain','utf-8')
        message['Subject'] = 'UPS Delivered Confirmation' 
        message['From'] = sender    
        message['To'] = receivers[0]  

        try:
            smtpObj = smtplib.SMTP('smtp.gmail.com:587') 
            #smtpObj.connect(mail_host, 587)
            #smtpObj.ehlo()
            smtpObj.starttls()
            #smtpObj.ehlo()
            smtpObj.login(mail_user, mail_pass) 
            smtpObj.sendmail(
                sender,receivers,message.as_string()) 
            smtpObj.quit() 
            print('success')
        except smtplib.SMTPException as e:
            print('error',e) 


def handle_deliveryMade(delivery, seq):
    global amazon_socket
    global world_socket

    #Return ACK
    return_ack(world_socket, delivery.seqnum)
    '''
    TO DO:

    1. Change the status of package (out for delivery -> delivered)  (FINISHED & TESTED)
    2. Tell the Amazon (UAPackageArrived) (FINISHED)
    3. Send the email
    '''

    packageid = delivery.packageid

    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("select packagestatus from ups_package where packageid='" + str(packageid) + "'")
    packages = cur.fetchall()

    # Only enter once
    for package in packages:
        if package[0] == "delivered":
            conn.commit()
            cur.close()
            conn.close()
            return

    # Connect to ups_package and then change the status of package_id
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("update ups_package set packagestatus='delivered' where packageid='" + str(packageid) + "'")

    uacommands = amazon_ups_pb2.UACommands()
    uap = uacommands.packagearrived.add()
    uap.shipid = packageid
    uap.seqnum = seq

    conn.commit()
    cur.close()
    conn.close()

    # Send UACommand to amazon
    send_msg(amazon_socket, uacommands.SerializeToString())
    print("[DEBUG] Sent UACommand package arrived to amazon")

    send_email(packageid)


def handle_finished(completion, seq):
    global amazon_socket
    global world_socket

    #Return ACK
    return_ack(world_socket, completion.seqnum)
    truck_id = completion.truckid

    '''
    TO DO (FINISHED & TESTED):
    Change the databse of ups_truck

    1.  If truck.status == on the way to warehouse
             on the way to warehouse -> arrived
             Tell the Amazon (UATruckArrived)
    
    2.  If truck.status == delivering
            delivering -> idle
    '''
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("select truckstatus from ups_truck where truckid='" + str(truck_id) + "'")
    trucks = cur.fetchall()

    '''
        TO DO (FINISHED):
        1.  Already know the truck id
        2.  Select ups_package where truck_id = truckid and status = 'created'
        3.  Get the shipid, change the status from 'created' to 'in the warehouse'
    '''

    # Only enter once
    for truck in trucks:
        if truck[0] == 'on the way to warehouse':
            cur.execute("update ups_truck set truckstatus='arrived at warehouse' where truckid='" + str(truck_id) + "'")

            uacommands = amazon_ups_pb2.UACommands()
            uat = uacommands.truckarrived.add()
            uat.truckid = truck_id
            uat.seqnum = seq

            cur.execute("select packageid from ups_package where truckid='" + str(truck_id) + "' and packagestatus='created'")
            packages = cur.fetchall()

            # Only enter once
            for package in packages:
                uat.shipid = package[0]
                cur.execute("update ups_package set packagestatus='in the warehouse' where packageid='" + str(package[0]) + "'")
            
            conn.commit()
            cur.close()
            conn.close()

            print("[DEBUG] Preparing to send UACommand truck is arrived " + str(truck_id))
            #send UACommand to amazon
            send_msg(amazon_socket, uacommands.SerializeToString())
            print("[DEBUG] Sent UACommand truck is arrived " + str(truck_id))
            
        elif truck[0] == 'delivering':
            cur.execute("update ups_truck set truckstatus='idle' where truckid='" + str(truck_id) + "'")
    
            conn.commit()
            cur.close()
            conn.close()


# Error detection
def handle_error_world(error, seq):
    global world_socket

    #Return ACK
    return_ack(world_socket, seq)

    print("[DEBUG] Error is " + error.err)


def return_ack(world_socket, ack):

    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    ucommands.acks.append(ack)

    #send UCommand to world
    send_msg(world_socket, ucommands.SerializeToString())
    #print("[DEBUG] Sent UCommand")
#===============================================================



#===============================================================
# Handle Amazon

# Go pickup action
# In a big function caused by UA protocol
# AUReqTruck
def go_pickup(truck_id, warehouse_id, seq):
    global world_socket
    global ack_set

    #Combine Information
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    pickup = ucommands.pickups.add()
    pickup.truckid = truck_id
    pickup.whid = warehouse_id
    pickup.seqnum = seq

    #send UCommand to world
    while True:
        send_msg(world_socket, ucommands.SerializeToString())
        print("[DEBUG] Sent UCommand go pick up")
        time.sleep(4)
        print(ack_set)
        if seq in ack_set:
            print("[DEBUG] Sent UCommand go pick up, already received by world")
            break
        print("[DEBUG] Sent UCommand go pick up, not received by world " + str(seq))


def handle_error_amazon(packageid, seq):
    global amazon_socket

    uacommands = amazon_ups_pb2.UACommands()
    uaerror = uacommands.uaerror.add()
    uaerror.err = "CANNOT ASSIGN TRUCKS NOW: " + str(packageid)
    uaerror.originseqnum = 0
    uaerror.seqnum = seq

    #send UACommand to amazon
    send_msg(amazon_socket, uacommands.SerializeToString())
    print("[DEBUG] Sent UACommand no truck")


def handle_truck_request(request, seq):
    global amazon_socket
    global world_socket
    global ack_set

    warehouse_id = request.warehouseid
    package_id = request.shipid
    order = request.orders
    destx = order.locationx
    desty = order.locationy
    description = order.description
    username = order.username

    '''
    ==================================================
    TO DO (FINISHED & TESTED):
    1. Go to the database to check the status of trucks (ups_truck), idle -> on the way to warehouse
    2. Find the proper status (idle, out for delivery)
    3. Change the status
    4. Go to the database (ups_packages), new corresponding package
        (...)
    '''
    # Connect to databse and and choose a truck to assign this work
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("select truckid from ups_truck where truckstatus='idle' or truckstatus = 'delivering'")
    trucks = cur.fetchall()

    if len(trucks):
        truckid = trucks[0][0]
        print("DEBUG] truckid is " + str(truckid))
        cur.execute("update ups_truck set truckstatus='on the way to warehouse' where truckid='" + str(truckid) + "'")

        conn.commit()
        cur.close()
        conn.close()

        # Connect to databse and and initialize this package
        conn = connect_to_database()
        cur = conn.cursor()
        cur.execute("insert into ups_package (owner, packageid, destx, desty, packagestatus, description, truckid, evaluation)\
                    values ('" + username + "', '" + str(package_id) + "', '" + str(destx) + "', '" + str(desty) + 
                    "', 'created', '" + description + "', '" + str(truckid) + "', 'none')")

        conn.commit()
        cur.close()
        conn.close()

        # Send the command to world
        go_pickup(truckid, warehouse_id, seq)

    else:
        handle_error_amazon(package_id, seq)


# Set delivery location
def set_delivery_location(delivery_location, package_id, X, Y):
    #Combine information
    delivery_location.packageid = package_id
    delivery_location.x = X
    delivery_location.y = Y
    

# Go deliver action
# In a big function caused by UA protocol
# AUTruckLoaded
def go_delivery(truck_id, package_id, seq):
    global amazon_socket
    global world_socket
    global ack_set

    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    delivery = ucommands.deliveries.add()
    delivery.truckid = truck_id
    print("[DEBUG] THE truck out for delivery is " + str(truck_id))
    delivery.seqnum = seq

    '''
    ==================================================
    TO DO (FINISHED & TESTED):

        **
            Package Status: created ----- in the warehouse ------- out for delivery ----- deliveried
        **

    1. Change the status of packageid from 2 to 3
    2. Find all the packages which status are 3 and truckid is truck_id 
    3. Get the required information

    '''

    # Connect to ups_package and then change the status of package_id to out for delivery
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("update ups_package set packagestatus='out for delivery' where packageid='" + str(package_id) + "'")

    # Find all the packages which status are 'out for delivery' and truckid is truck_id 
    cur.execute("select packageid, destx, desty from ups_package where truckid='" + str(truck_id) + "' and packagestatus='out for delivery'")
    packages = cur.fetchall()

    # Change the status of truck from 'arrived at warehouse' to 'delivering'
    cur.execute("update ups_truck set truckstatus='delivering' where truckid='" + str(truck_id) + "'")

    conn.commit()
    cur.close()
    conn.close()


    for package in packages:
        delivery_location = delivery.packages.add()
        set_delivery_location(delivery_location, package[0], package[1], package[2])
    
    print("[DEBUG] Finish preparation of UCommand go delivery")

    #send UCammand to world
    while True:
        send_msg(world_socket, ucommands.SerializeToString())
        print("[DEBUG] Sent UCommand go delivery")
        time.sleep(4)
        if seq in ack_set:
            print("[DEBUG] Sent UCommand go delivery, already recceived by world")
            break
        print("[DEBUG] Sent UCommand go delivery, not recceived by world " + str(seq))


def handle_truck_loaded(loaded, seq):
    global amazon_socket
    global world_socket

    truck_id = loaded.truckid
    package_id = loaded.shipid

    go_delivery(truck_id, package_id, seq)

#===============================================================


# The second step: Connect to amazon
def get_amazon_socket():
    client_amazon_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_amazon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ip_port = ('vcm-13673.vm.duke.edu', 43210)
    try:
        client_amazon_socket.connect(ip_port)
        print("Socket Connected")
        return client_amazon_socket
    except socket.error:
        print("Caught exception socket.error")

def connect_to_amazon(worldid):
    global seq
    global amazon_socket

    lock.acquire()
    seqNum = seq
    seq += 1
    lock.release()

    uaw = amazon_ups_pb2.UAWorldBuilt()
    uaw.worldid = worldid
    uaw.seqnum = seqNum

    # Send UAWorldBuilt to amazon
    send_msg(amazon_socket, uaw.SerializeToString())
    print("[DEBUG] Sent UAWorldBuilt")


# The first step: start connection with world
# It needs to initialize the table in database (truck) and wait for the response from world
def get_world_socket():
    client_world_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_world_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ip_port = ('vcm-13673.vm.duke.edu', 12345)
    try:
        client_world_socket.connect(ip_port)
        print("Socket Connected")
        return client_world_socket
    except socket.error:
        print("Caught exception socket.error")


def connect_to_world(truck_number):
    global world_socket
    uconnect = world_ups_pb2.UConnect()
    uconnect.isAmazon = False

    '''
    ===============================================================
    TO DO (FINISHED & TESTED):
    
    1. Finish the database, initialize the truck table.
    2. Do not forget to drop the original table.

    '''

    # Connect to databse and initialize the table   
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("truncate table ups_package;")
    cur.execute("truncate table ups_truck;")
    
    for num in range(1, truck_number + 1):
        truck = uconnect.trucks.add()
        truck.id = num
        truck.x = 1
        truck.y = 1

        cur.execute("insert into ups_truck (truckid, truckstatus) values ('" + str(num) + "', 'idle')")
 
    conn.commit()
    cur.close()
    conn.close()
    

    #send UConnect to world
    send_msg(world_socket, uconnect.SerializeToString())
    print("[DEBUG] Sent UConnect")

    #receive UConnected from world
    received = receive_msg(world_socket)

    uconnected = world_ups_pb2.UConnected()
    uconnected.ParseFromString(received)
    worldid = uconnected.worldid

    print("[DEBUG] Received MSG: " + uconnected.result)
    return worldid


def connect_to_world_again(truck_number, world_id):
    global world_socket
    uconnect = world_ups_pb2.UConnect()
    uconnect.isAmazon = False
    uconnect.worldid = world_id

    #send UConnect to world
    send_msg(world_socket, uconnect.SerializeToString())
    print("[DEBUG] Sent UConnect")

    #receive UConnected from world
    received = receive_msg(world_socket)

    uconnected = world_ups_pb2.UConnected()
    uconnected.ParseFromString(received)

    print("[DEBUG] Received MSG: " + uconnected.result)



# Handle the message from world
def handle_world_response():
    global seq
    global amazon_socket
    global world_socket
    global ack_set
    global setlock
    global worldid

    #receive UResponses from world
    received = receive_msg(world_socket)
    print("[DEBUG] Receive UResponses")
    if len(received) == 0:
        print("Empty message")
        world_socket = get_world_socket()
        connect_to_world_again(10, worldid)
        return

    uresponses = world_ups_pb2.UResponses()
    uresponses.ParseFromString(received)

    if(uresponses.finished == True):
        print("[DEBUG] finished by world")

    for delivery in uresponses.delivered:
        print("[DEBUG] Receive UResponses delivered")
        lock.acquire()
        seqNum = seq
        seq += 1
        lock.release()
        t = threading.Thread(target = handle_deliveryMade,
                            args = (delivery, seqNum))
        t.start()

    for completion in uresponses.completions:
        print("[DEBUG] Receive UResponses finished")
        lock.acquire()
        seqNum = seq
        seq += 1
        lock.release()
        t = threading.Thread(target = handle_finished,
                            args = (completion, seqNum))
        t.start()

    for ack in uresponses.acks:
        print("[DEBUG] World ACK is " + str(ack))
        setlock.acquire()
        ack_set.add(ack)
        print(ack_set)
        setlock.release()
        

    for error in uresponses.error:
        print("[DEBUG] Receive UResponses error")
        lock.acquire()
        seqNum = seq
        seq += 1
        lock.release()
        t = threading.Thread(target = handle_error_world,
                            args = (error, seqNum))
        t.start()

    for t in uresponses.truckstatus:
        print("[DEBUG] TRUCKSTATUS " + str(t.truck_id) + "  "+ t.status)


# Handle the message from amazon
def handle_amazon_response():
    global seq
    global world_socket
    global amazon_socket

    #receive UResponses from world
    received = receive_msg(amazon_socket)
    print("[DEBUG] Receive UAResponses")
    if len(received) == 0:
        print("Empty message")
        return
        
    uaresponses = amazon_ups_pb2.AUCommands()
    uaresponses.ParseFromString(received)

    for request in uaresponses.requests:
        print("[DEBUG] Receive UAResponses truck request")
        lock.acquire()
        seqNum = seq
        seq += 1
        lock.release()
        t = threading.Thread(target = handle_truck_request,
                            args = (request, seqNum))
        t.start()
    
    for loaded in uaresponses.truckloaded:
        print("[DEBUG] Receive UAResponses truck loaded")
        lock.acquire()
        seqNum = seq
        seq += 1
        lock.release()
        t = threading.Thread(target = handle_truck_loaded,
                            args = (loaded, seqNum))
        t.start()

    for ack in uaresponses.acks:
        print("[DEBUG] Amazon ACK is " + str(ack))

    for error in uaresponses.uaerror:
        print("[DEBUG] Amazon error")


def main():
    global seq
    global lock
    global world_socket
    global amazon_socket
    global ack_set
    global setlock
    global worldid

    world_socket = get_world_socket()
    worldid = connect_to_world(10)
    print("world id is " + str(worldid))
  
    amazon_socket = get_amazon_socket()
    connect_to_amazon(worldid)
    
    while True:
        possible_sockets = [world_socket, amazon_socket]
        readable, writable, exceptional = select.select(possible_sockets, [], [])
        print("len is " + str(len(readable)))
        '''
        if(len(readable) == 0):
            print("Not receive anything")
            continue
        '''
        
        for s in readable:
            if s is world_socket:
                time.sleep(0.5)
                print("[DEBUG] This is the message from world")
                handle_world_response()
            else:
                time.sleep(0.5)
                print("[DEBUG] This is the message from amazon")
                handle_amazon_response()
        
        '''
    TO DO (FINISHED):
    1.  Connect to Amazon (UAWorldBuilt) (FINISHED)
    2.  select()
            seqNum++
            
    3.  Multi_thread
        If inforamtion from Amazon (go_pickup && go_delivery)
        If information from World (2 handles)
    '''

     
    
if __name__ == "__main__":
    main()

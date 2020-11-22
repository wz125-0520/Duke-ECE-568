import psycopg2
import socket
import world_ups_pb2, amazon_ups_pb2
import sys
import threading
import select
from basic import connect_to_database, send_msg
import smtplib
from email.mime.text import MIMEText

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


def handle_deliveryMade(amazon_socket, world_socket, delivery, seq):
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


def handle_finished(amazon_socket, world_socket, completion, seq):
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
            
        else:
            cur.execute("update ups_truck set truckstatus='idle' where truckid='" + str(truck_id) + "'")
    
            conn.commit()
            cur.close()
            conn.close()


# Error detection
def handle_error_world(world_socket, error, seq):
    #Return ACK
    return_ack(world_socket, seq)

    print("[DEBUG] Error is " + error.err)


def return_ack(world_socket, ack):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    #???????
    # Not quite sure whether it is correct or not
    ucommands.acks.append(ack)

    #send UCommand to world
    send_msg(world_socket, ucommands.SerializeToString())
    #print("[DEBUG] Sent UCommand")
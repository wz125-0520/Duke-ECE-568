import psycopg2
import socket
import world_ups_pb2, amazon_ups_pb2
import sys
import threading
import select
from basic import send_msg, connect_to_database

# Go pickup action
# In a big function caused by UA protocol
# AUReqTruck
def go_pickup(world_socket, truck_id, warehouse_id, seq):
    #Combine Information
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    pickup = ucommands.pickups.add()
    pickup.truckid = truck_id
    pickup.whid = warehouse_id
    pickup.seqnum = seq

    #send UCommand to world
    send_msg(world_socket, ucommands.SerializeToString())
    print("[DEBUG] Sent UCommand go pick up")


def handle_error_amazon(amazon_socket, packageid, seq):
    uacommands = amazon_ups_pb2.UACommands()
    uaerror = uacommands.uaerror.add()
    uaerror.err = "CANNOT ASSIGN TRUCKS NOW: " + str(packageid)
    uaerror.originseqnum = 0
    uaerror.seqnum = seq
    #send UACommand to amazon
    send_msg(amazon_socket, uacommands.SerializeToString())
    print("[DEBUG] Sent UACommand no truck")


def handle_truck_request(amazon_socket, world_socket, request, seq):
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

        # Send the command to world
        go_pickup(world_socket, truckid, warehouse_id, seq)

        # Connect to databse and and initialize this package
        conn = connect_to_database()
        cur = conn.cursor()
        cur.execute("insert into ups_package (owner, packageid, destx, desty, packagestatus, description, truckid, evaluation)\
                    values ('" + username + "', '" + str(package_id) + "', '" + str(destx) + "', '" + str(desty) + 
                    "', 'created', '" + description + "', '" + str(truckid) + "', 'none')")

        conn.commit()
        cur.close()
        conn.close()
    else:
        handle_error_amazon(amazon_socket, package_id, seq)


# Set delivery location
def set_delivery_location(delivery_location, package_id, X, Y):
    #Combine information
    delivery_location.packageid = package_id
    delivery_location.x = X
    delivery_location.y = Y
    

# Go deliver action
# In a big function caused by UA protocol
# AUTruckLoaded
def go_delivery(world_socket, truck_id, package_id, seq):
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
    send_msg(world_socket, ucommands.SerializeToString())
    print("[DEBUG] Sent UCommand go delivery")


def handle_truck_loaded(amazon_socket, world_socket, loaded, seq):
    truck_id = loaded.truckid
    package_id = loaded.shipid

    go_delivery(world_socket, truck_id, package_id, seq)
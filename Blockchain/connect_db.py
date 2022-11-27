import sqlite3

def setup():
    connect = sqlite3.connect("dbs/nodes.db")
    db = connect.cursor()
    db.execute("""CREATE TABLE IF NOT EXISTS nodes 
                    (ip VARCHAR(50), port VARCHAR(50), 
                    UNIQUE(ip, port))""")
    db.execute("""CREATE TABLE IF NOT EXISTS explore_nodes 
                    (ip VARCHAR(50), port VARCHAR(50), connections INT,
                    UNIQUE(ip, port))""")

    connect.commit()
    db.close()


def insert_node(ip, port):
    connect = sqlite3.connect("dbs/nodes.db")
    db = connect.cursor()
    try:
        
        db.execute(f"INSERT INTO nodes(ip,port) VALUES('{ip}','{port}')") #Fix sql injection, maybe
        connect.commit()
        db.close()
    except Exception as E:
        print("insert error: ",E)
        if 'no such table' in E.args[0]:
            setup()
            
    finally:
        if connect:
            connect.close()

def remove_node(ip, port):
    connect = sqlite3.connect("dbs/nodes.db")
    db = connect.cursor()
    try:
        
        db.execute(f"DELETE FROM nodes where ip = '{ip}' AND port = '{port}'") #Fix sql injection, maybe
        connect.commit()
        db.close()
    except Exception as E:
        print("remove node error: ",E)
        if 'no such table' in E.args[0]:
            setup()
            
    finally:
        if connect:
            connect.close()
def remove_explore_node(ip, port):
    connect = sqlite3.connect("dbs/nodes.db")
    db = connect.cursor()
    try:
        
        db.execute(f"DELETE FROM explore_nodes where ip = '{ip}' AND port = '{port}'") #Fix sql injection, maybe
        connect.commit()
        db.close()
    except Exception as E:
        print("remove explore error: ",E)
        if 'no such table' in E.args[0]:
            setup()
            
    finally:
        if connect:
            connect.close()

def insert_explore_node(ip, port, connections):
    
    try:
        connect = sqlite3.connect("dbs/nodes.db")
        db = connect.cursor()
        try:
            db.execute(f"INSERT INTO explore_nodes(ip,port,connections) VALUES('{ip}','{port}', {0})")
        except:
            ...
        db.execute(f"""UPDATE explore_nodes
                SET connections = {connections}
                    
                WHERE
                    ip = '{ip}' AND port = '{port}';""")
                        #Fix sql injection, maybe
        connect.commit()
        db.close()
    except Exception as E:
        print(E)
        setup()
       

            
    finally:
        if connect:
            connect.close()

def explore_nodes():
    connect = sqlite3.connect("dbs/nodes.db")
    db = connect.cursor()
    try:   
        db.execute("SELECT * FROM explore_nodes")
        nodes = []
        for i in db.fetchall():
            nodes.append(i)


        nodes.sort(key = lambda x: x[2])
        
            
        db.close()
        return nodes


    except Exception as E:
        print("explore node error ", E)
        setup()
def get_nodes():
    connect = sqlite3.connect("dbs/nodes.db")
    db = connect.cursor()
    try:   
        db.execute("SELECT * FROM nodes")
        nodes = []
        for i in db.fetchall():
            nodes.append(i)


        nodes.sort(key = lambda x: x[2])
        
            
        db.close()
        return nodes


    except Exception as E:
        print("get node error", E)
        
        setup()
        print(E)
        return []
       
def view_table(table):
    connect = sqlite3.connect("dbs/nodes.db")
    db = connect.cursor()
    try:
        
        db.execute(f"SELECT * FROM {table}")
        print(db.fetchall())
        for i in db.fetchall():
            print(i)
        db.close()

    except Exception as E:
        setup()

    finally:
        if connect:
            connect.close()
insert_node("1231", "2")
insert_explore_node("12321","2",10)

view_table("explore_nodes")
view_table("nodes")
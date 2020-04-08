package edu.duke.ece568.infrastructure;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.net.UnknownHostException;

public class ClientInfrastructureTest { 

    @Test
    public void testInit() { 
        
    }
    
    @Test
    public void testSendRequest() { 
        
    }
    
    @Test
    public void testConfigClient() throws IOException {
        ClientInfrastructure client = new ClientInfrastructure();
        client.configClient();
        assertEquals(12345, client.port);
    }
    
    @Test
    public void testGetHostByName() throws UnknownHostException {
        ClientInfrastructure client = new ClientInfrastructure();
        assertEquals("127.0.0.1", client.getHostByName("localhost"));
    }
    
    @Test
    public void testMain() { 
        
    }
    

} 

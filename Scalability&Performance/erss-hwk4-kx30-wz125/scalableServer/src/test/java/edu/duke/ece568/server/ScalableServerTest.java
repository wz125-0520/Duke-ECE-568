package edu.duke.ece568.server;

import static org.junit.jupiter.api.Assertions.*;

import org.json.JSONObject;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;

public class ScalableServerTest { 

    @Test
    public void testInit() { 
        
    }
    
    @Test
    public void testRun() { 
        
    }
    
    @Test
    public void testRunPerCreateThread() { 
        
    }
    
    @Test
    public void testRunThreadPerRequest() { 
        
    }
    
    @Test
    public void testHandleIncomeRequest() { 
        
    }
    
    @Test
    public void testAddToBucket() {
        ScalableServer scalableServer = new ScalableServer(null);
        scalableServer.bucket = new ArrayList<>(Collections.nCopies(5, 0L));
        assertThrows(IllegalArgumentException.class, () -> {scalableServer.addToBucket(10, 1);});
        assertEquals(1, scalableServer.addToBucket(1, 1));
    }
    
    @Test
    public void testDelay() { 
        ScalableServer scalableServer = new ScalableServer(null);
        Instant start = Instant.now();
        scalableServer.delay(3);
        Instant end = Instant.now();
//        assertEquals(3, Duration.between(start, end).toSeconds());
    }
    
    @Test
    public void testReadConfigurationFile() throws IOException {
        /*ScalableServer scalableServer = new ScalableServer(null);
        JSONObject jsonObject = new JSONObject(scalableServer.readConfigurationFile());
        assertTrue(jsonObject.has("preCreateThread"));
        assertTrue(jsonObject.has("bucketSize"));
        assertTrue(jsonObject.has("comment"));*/
    }
    
    @Test
    public void testMain() { 
        
    }

} 

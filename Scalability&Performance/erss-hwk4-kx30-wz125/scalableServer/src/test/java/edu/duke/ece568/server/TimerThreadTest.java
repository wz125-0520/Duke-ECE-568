package edu.duke.ece568.server;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

public class TimerThreadTest { 

    @Test
    public void testRun() throws InterruptedException {
        Info info = new Info();
        TimerThread timerThread = new TimerThread(info);
        timerThread.start();
        for (int i = 0; i < 120; i++){
            Thread.sleep(100);
            synchronized (this) {
                info.addRequestCnt();
            }
        }
    }
    
    @Test
    public void testLogData() { 
        
    }
    
    @Test
    public void testHashCode() { 
        
    }
    
    @Test
    public void testEquals() { 
        
    }
    
    @Test
    public void testUncaughtException() { 
        
    }
    

} 

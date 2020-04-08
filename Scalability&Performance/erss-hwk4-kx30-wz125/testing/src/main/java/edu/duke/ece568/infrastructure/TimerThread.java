package edu.duke.ece568.infrastructure;

import java.io.IOException;
import java.util.Timer;
import java.util.TimerTask;

/**
 * This is the timer thread, which will log the latest data into data.log file every 30 seconds.
 */
public class TimerThread extends Thread {
    // the time period we log data, in seconds
    private static final int TIME_PERIOD = 5;

    Info info;

    public TimerThread(Info info) {
        this.info = info;
    }

    @Override
    public void run() {
        Timer timer = new Timer();
        TimerTask task = new TimerTask() {
            @Override
            public void run() {
                logData();
            }
        };
        // schedule is in milliseconds
        timer.schedule(task, TIME_PERIOD * 1000, TIME_PERIOD * 1000);
    }

    void logData(){
        Info tmp = null;
        synchronized (this) {
            // make a copy to reduce the lock granularity
            tmp = new Info(info);
            info.resetInfo();
        }
        System.out.println(tmp.getRequestCnt());
    }
}

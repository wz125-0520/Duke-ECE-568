package edu.duke.ece568.server;

import java.io.BufferedWriter;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;

/**
 * Logger class, responsible to log the data to log file.
 */
public class Logger {
    private static final String LOG_FILE = "./data.log";

    public Logger() throws IOException {
        emptyLog();
    }

    /**
     * This function will empty the log file(i.e. delete everything inside).
     * @throws IOException probably file not exist
     */
    public void emptyLog() throws IOException {
        FileOutputStream myOutput = new FileOutputStream(LOG_FILE);
        myOutput.write("".getBytes());
    }

    /**
     * This function will log the info instance into the logger file.
     * @param info info we care
     * @throws IOException probably file not exist
     */
    public void log(Info info) throws IOException {
        String content = String.format("request cnt: %d\n", info.getRequestCnt());
	System.out.println(content);
        BufferedWriter out = new BufferedWriter(new FileWriter(LOG_FILE, true));
        out.write(content);
        out.close();
    }
}

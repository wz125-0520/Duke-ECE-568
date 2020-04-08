package edu.duke.ece568.server;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;

public class ScalableServer {
    private static final String INIT_INFO = "ScalableServer is running, waiting for new connection...";

    boolean perCreate;
    Server server;
    List<Long> bucket;
    Info info;
    TimerThread timerThread;
    int queueSize;

    public ScalableServer(Server server){
        this.server = server;
        this.info = new Info();
        this.timerThread = new TimerThread(this.info);
    }

    public void configServer() throws IOException {
        String configName = "../configuration.json";
        StringBuilder contentBuilder = new StringBuilder();
        try(Stream<String> stream = Files.lines(Paths.get(configName))) {
            stream.forEach(s -> contentBuilder.append(s).append("\n"));
        }
        JSONObject jsonObject = new JSONObject(contentBuilder.toString());
        int bucketSize = jsonObject.optInt("bucketSize", 32);
        this.perCreate = jsonObject.optJSONObject("server").optBoolean("preCreateThread", false);
        // how many thread client will open
        this.queueSize = jsonObject.optInt("threadCnt", 10);
        // initialize the bucket of all 0
        this.bucket = new ArrayList<>(Collections.nCopies(bucketSize, 0L));
    }

    public void run() {
        System.out.println(INIT_INFO);
        // start collecting data
        this.timerThread.start();
        if (perCreate){
            runPerCreateThread();
        }else {
            runThreadPerRequest();
        }
    }

    public void runPerCreateThread(){
        BlockingQueue<Runnable> workQueue = new LinkedBlockingQueue<>(queueSize + 20);
        ThreadPoolExecutor threadPool = new ThreadPoolExecutor(100, 150, 5, TimeUnit.SECONDS, workQueue);

        while (!Thread.currentThread().isInterrupted()){
            Socket socket = server.accept();
            if (socket != null){
                threadPool.execute(()-> handleIncomeRequest(socket));
            }
        }
    }

    public void runThreadPerRequest(){
        while (!Thread.currentThread().isInterrupted()){
            Socket socket = server.accept();
            if (socket != null){
                new Thread(() -> handleIncomeRequest(socket)).start();
            }
        }
    }

    void handleIncomeRequest(Socket socket) {
        try {
            socket.setSoTimeout(5000);
            // get the input & output stream
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter out = new PrintWriter(socket.getOutputStream());
            // get the actual request
            String request = in.readLine();
            String[] data = request.split(",");
            int delayTime = Integer.parseInt(data[0]);
            int index = Integer.parseInt(data[1]);
            delay(delayTime);
            long result = addToBucket(index, delayTime);
            out.println(result);
            out.flush();
            // count one valid request
            info.addRequestCnt();
	        socket.close();
        }catch (Exception ignored){
            // illegal incoming request, simply ignore it(don't count this in total request)
        }
    }

    /**
     * This function will delay a few seconds and then add the delay count to the corresponding bucket
     * @param index index of the bucket
     * @param val the value add to the bucket
     * @return the latest bucket value(after adding the delay count to bucket)
     */
    long addToBucket(int index, int val){
        if (index >= bucket.size()){
            throw new IllegalArgumentException("Don't have these much of buckets, check your configuration file");
        }
        long oldVal = bucket.get(index);
        synchronized (this) {
            // we probably only need to lock for write
            bucket.set(index, oldVal + val);
        }
        return bucket.get(index);
    }

    /**
     * This function will delay "second" seconds
     * @param second the amount of seconds delay
     */
    void delay(int second){
        long startTime = System.currentTimeMillis();
        // convert second to milliseconds
        long reqDelay = second * 1000;
        long elapsed = 0;
        while (elapsed <= reqDelay){
            elapsed = System.currentTimeMillis() - startTime;
        }
    }

    public static void main(String[] args) throws IOException {
        ScalableServer scalableServer = new ScalableServer(new Server());
        scalableServer.configServer();
        scalableServer.run();
    }
}

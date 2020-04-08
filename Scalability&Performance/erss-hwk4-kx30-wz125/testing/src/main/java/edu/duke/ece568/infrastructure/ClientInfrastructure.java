package edu.duke.ece568.infrastructure;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Random;
import java.util.stream.Stream;

public class ClientInfrastructure {
    String host;
    int port;
    int bucketSize;
    int threadCnt;
    int maxDelay;
    TimerThread timerThread;
    Info info;

    ClientInfrastructure(){
        info = new Info();
        timerThread = new TimerThread(info);
    }

    /**
     * This function will read the configuration file and then config the client.
     * @throws IOException probably because of file not exist
     */
    public void configClient() throws IOException {
        // read configuration file
        String configName = "../configuration.json";
        StringBuilder contentBuilder = new StringBuilder();
        try(Stream<String> stream = Files.lines(Paths.get(configName))) {
            stream.forEach(s -> contentBuilder.append(s).append("\n"));
        }
        // get data from json
        JSONObject jsonObject = new JSONObject(contentBuilder.toString());
        JSONObject jsonClient = jsonObject.getJSONObject("client");
        this.host = jsonClient.optString("host", "localhost");
        this.port = jsonClient.optInt("port", 12345);
        this.maxDelay = jsonClient.optInt("maxDelay", 3);
        // bucket size  & threadCnt are a share configuration variable between server and client
        this.bucketSize = jsonObject.optInt("bucketSize", 32);
        this.threadCnt = jsonObject.optInt("threadCnt", 90);

        System.out.println("Max delay: " + maxDelay);
        System.out.println("Bucket size: " + bucketSize);
        System.out.println("Thread Cnt: " + threadCnt);
    }

    void run() {
        timerThread.start();
        for (int i = 0; i < threadCnt; i++){
            new Thread(() -> {
                // use current time as seed
                Random rand = new Random(System.currentTimeMillis());
                while (true){
                    int delay = rand.nextInt(maxDelay + 1);
                    int bucket = rand.nextInt(bucketSize);
                    sendRequest(delay, bucket);
                }
            }).start();
        }
        // let the client stuck here, keep sending request
        while (!Thread.currentThread().isInterrupted()){}
    }

    /**
     * This function will construct a socket, send request and receive response.
     * @param delay delay time
     * @param index index of bucket
     */
    void sendRequest(int delay, int index) {
        try {
            // blocking connect
            Socket socket = new Socket(host, port);
            // if the server doesn't response in 1 min, we discard this result
            socket.setSoTimeout(60 * 1000);
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter out = new PrintWriter(socket.getOutputStream());
            out.println(String.format("%d,%d\n", delay, index));
            out.flush();
            // receive response
            String res = in.readLine();
            info.addRequestCnt();
            socket.close();
        }catch (Exception ignored){
        }
    }

    /**
     *  This function translate the host name to its corresponding IP address.
     * @param hostStr string of the host name
     * @return the corresponding IP address
     * @throws UnknownHostException if the host is invalid
     */
    String getHostByName(String hostStr) throws UnknownHostException {
        InetAddress addr = InetAddress.getByName(hostStr);
        return addr.getHostAddress();
    }

    public static void main(String[] args) throws IOException {
        ClientInfrastructure client = new ClientInfrastructure();
        client.configClient();
        client.run();
    }
}

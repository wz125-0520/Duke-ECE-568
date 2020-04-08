package edu.duke.ece568.server;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

import static org.junit.jupiter.api.Assertions.*;

public class CommunicationTest {
    private static final int SLEEP_TIME = 500;
    private static final int PORT = 8080;
    static Server server;

    @BeforeAll
    static void beforeAll() throws InterruptedException {
        // initialize the server
        new Thread(() -> {
            try {
                server = new Server(PORT);
            } catch (IOException ignored) {
            }
        }).start();
        // pause to give the server some time to setup
        Thread.sleep(SLEEP_TIME);
    }

    @Test
    public void testAccept() throws IOException {
        String msgCTS = "Hello server";
        String msgSTC = "Hi client";

        new Thread(() -> {
            try {
                Socket socket = server.accept();
                assertNotNull(socket);
                BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                PrintWriter out = new PrintWriter(socket.getOutputStream());
                out.println(msgSTC);
                out.flush();
                assertEquals(msgCTS, in.readLine());
            } catch (IOException ignored) {
            }
        }).start();
        Socket socket = new Socket("127.0.0.1", PORT);
        BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        PrintWriter out = new PrintWriter(socket.getOutputStream());
        assertEquals(msgSTC, in.readLine());
        out.println(msgCTS);
        out.flush();
    }
    
    @Test
    public void testAcceptNull() throws IOException {
        Server s = new Server();
        s.serverSocket.close();
        assertNull(s.accept());
    }
} 

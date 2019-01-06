import java.io.*;
import java.net.*;
import java.util.*;

/*
 * This code is edited by MEISI LI.
 * The student id is z5119623
 * Client to process ping requests over UDP. 
 */

public class PingClient {

    public static void main(String args[]) throws Exception {
        if (args.length < 2) {
            System.out.println("Required arguments: host, port");
            return;
        }

        String ServerName = args[0];
        int port = Integer.parseInt(args[1]);

        /*
         * Create a datagram socket to receive and send UDP packets
         */
        InetAddress server = InetAddress.getByName(ServerName);
        DatagramSocket socket = new DatagramSocket();

        long minTime = 0;
        long maxTime = 0;
        long aveTime = 0;

        /* 
         * sends 10 ping requests to the server, 
         * separated by approximately one second
         */
        for (int i = 0; i < 10; i++) {
            long sendTime = System.currentTimeMillis();

            /*
             * Each message contains a payload of data that 
             * includes the keyword PING, a sequence number, and a timestamp.
             */
            String str = "PING " + i + " " + sendTime + " \n";
            byte[] buffer = new byte[1024];
            buffer = str.getBytes();

            // Create a datagram packet to hold incoming UDP packet.
            DatagramPacket request = new DatagramPacket(buffer, buffer.length, server, port);
            socket.send(request);

            DatagramPacket response = new DatagramPacket(new byte[1024], 1024);

            try {
                socket.setSoTimeout(1000);  // 1 second

                // Try to receive the response from the server
                socket.receive(response);

                // Timestamp 
                long receiveTime = System.currentTimeMillis();

                long spendTime = receiveTime - sendTime;

                if (i == 0) {
                    minTime = spendTime;
                    maxTime = spendTime;
                }

                if (spendTime < minTime)    minTime = spendTime;
                if (spendTime > maxTime)    maxTime = spendTime;

                // Calculate average delay.
                aveTime = ((spendTime / (i + 1)) + aveTime);

                byte[] buf = request.getData();
                ByteArrayInputStream bais = new ByteArrayInputStream(buf);
                InputStreamReader isr = new InputStreamReader(bais);
                BufferedReader br = new BufferedReader(isr);
                String line = br.readLine();

                System.out.println( "ping to " + response.getAddress().getHostAddress() + ", " + 
                        new String(line) + "\r\n" + " seq = " + i + ", rtt = " + spendTime + " ms");


            } catch (IOException e) {
                // Print which packet has timeout
                System.out.println( "ping to " + ServerName + 
                    ", PING " + i + "\n seq = " + i + ", time out");
            }
        }

        System.out.println("min rtt = " + minTime + " ms" + ", max rtt = " + maxTime 
                + " ms" + ", average rtt = " + aveTime + " ms");
        socket.close();

    }

}

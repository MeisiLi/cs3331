import java.io.*;
import java.net.*;
import java.util.*;
import java.util.regex.*;

public class WebServer {
    public static void main(String[] args) {

        if (args.length != 1) {
            System.out.println("Required arguments: port");
            return;
        }
        // Get the port number
        int portNumber = Integer.parseInt(args[0]);

        System.out.print("Start: ");

        // Only process GET request.
        Pattern r = Pattern.compile("^GET .*");

        try {
            // Set up server
            ServerSocket socket = new ServerSocket(portNumber);

            // Processing loop. Listen on the port number
            while (true) {
                try {
                    // Set up client
                    // (i) create a connection socket when contacted by a client (browser).
                    Socket client = socket.accept();
                    System.out.println("Accepted");

                    // Reads inputstream from client
                    BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));
                    // Process request
                    String line;
                    while((line = in.readLine()) != null) {
            
                        // (ii) receive HTTP request from this connection.
                        // (iii) determine the specific file being requested.
                        String requestedResource = null;
                        
                        BufferedWriter outStream = new BufferedWriter(new OutputStreamWriter(client.getOutputStream()));
                    
                        if(line.length() == 0)
                            break;
                        Matcher m = r.matcher(line);
                        // when the header is GET
                        if(m.find()) {
                            requestedResource = line.split(" /")[1];
                            requestedResource = requestedResource.split(" HTTP")[0];

                            System.out.println("Request resource is: " + requestedResource);

                            File file = new File(requestedResource);

                            String content = file.toString();
                            System.out.println("content: " + content);

                            DataOutputStream writer = new DataOutputStream(client.getOutputStream());

                            if(file.exists()) {
                                // Point to outputstream from client
                                FileInputStream fis = new FileInputStream(file);
                                byte[] data = new byte[(int) file.length()];
                                fis.read(data);
                                fis.close();

                                System.out.println("Open the file " + content);
                                // return the file
                                // (v) an HTTP response message 
                                writer.writeBytes("HTTP/1.1 200 OK\r\nContent-Type: " + contentType(content) + "\r\n");
                                writer.writeBytes("Content-Length: " + data.length + "\r\n\r\n");
                                //writer.writeBytes("ok");
                                writer.write(data);
                            } else {
                                // return 404
                                System.out.println("File does not exist!");
                                // (v) an HTTP response message 
                                writer.writeBytes("HTTP/1.1 200 OK\r\nContent-type: text/html\r\n");
                                writer.writeBytes("Content-Length: " + 9 + "\r\n\r\n");
                                writer.writeBytes("Not Found");
                            }
                            // close client
                            writer.flush();
                            writer.close();
                        }
                    }

                } catch(IOException e) {
                    e.printStackTrace();
                }
            }

        } catch(IOException e) {
            System.out.println("Failed to attach to port");
            e.printStackTrace();
        }

    }

    private static String contentType(String fileName) {
        if(fileName.endsWith(".html")) {return "text/html";}
        if(fileName.endsWith(".png")) {return "image/png";}
        // if(fileName.endsWith(".gif")) {return "image/gif";}
        return "application/octet-stream";
    }
}

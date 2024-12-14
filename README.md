# HTTP Server

![HTTP Server Logo](path-to-logo)

## Introduction
This project implements a simple multithreaded HTTP/1.1 compliant web server designed to handle various HTTP requests (GET, POST, PUT, DELETE, etc.), manage cookies, support multipart form data, and handle basic logging and error management. This server was built to explore the inner workings of the HTTP protocol, server design, and request handling, and is based on the HTTP/1.1 RFC 2616.

---

## Features

1. **HTTP Methods Implementation**  
   - Supports core HTTP methods including `GET`, `POST`, `PUT`, `DELETE`, `HEAD`.

2. **Multipart Form Data Handling**  
   - Ability to process multipart form data for file uploads and form submissions.

3. **Logging**  
   - Implements **access logs** and **error logs** to track request details and server issues.

4. **Customized Configuration File**  
   - Allows server configuration through a user-friendly `.conf` file.

5. **Cookies**  
   - Support for setting and retrieving cookies between the client and server for session management.

6. **Access Logs**  
   - Provides detailed logs of all incoming requests, including IP address, request time, and response status.

7. **Error Logs**  
   - Detailed logging of any errors, including error types and affected resources.

---

## Instructions

### 1. Starting the Server

To start the server, use the following command:

```bash
bash start.sh

### 2.Stopping the Server

To stop  the server, use the following command:

```bash
bash start.sh

### 3.Run the testcases

```bash
python testing.py



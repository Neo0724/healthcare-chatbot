import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:socket_io_client/socket_io_client.dart' as socket_io;

class SocketService {
  late socket_io.Socket socket;

  void connect(String conversationId, Function handleIncomingMessage) {
    socket = socket_io.io(
      dotenv.get("API_URL"),
      socket_io.OptionBuilder()
          .setTransports(['websocket'])
          .enableAutoConnect()
          .build(),
    );

    socket.onConnect((_) {
      print("Connected");

      // Join conversation room
      socket.emit("join_room", {"conversation_id": conversationId});
    });

    // Listen for AI messages
    socket.on("message", (data) {
      handleIncomingMessage(data);
    });

    socket.onDisconnect((_) {
      print("Disconnected");
    });
  }

  void disconnect() {
    socket.dispose();
  }
}

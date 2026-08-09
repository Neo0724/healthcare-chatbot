import 'package:chatbot/widgets/side_drawer.dart';
import 'package:chatbot/router/app_router.dart';
import 'package:chatbot/utils/custom_dio.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

class NewConversation extends StatefulWidget {
  const NewConversation({super.key});

  @override
  State<NewConversation> createState() => _NewConversationState();
}

class _NewConversationState extends State<NewConversation> {
  final _messageController = new TextEditingController();

  Future<void> _handleSendMessage() async {
    try {
      final response = await CustomDio.getCustomDio().post(
        "/create_conversation",
        data: {"user_input": _messageController.text},
      );

      if (response.statusCode == 200 && response.data["success"]) {
        final String conversationId = response.data["conversation_id"];
        appRouter.goNamed(
          "conversation",
          pathParameters: {"id": conversationId},
          queryParameters: {"redirectFromNew": "true"},
        );
      }
    } on DioException catch (e) {
      debugPrint("Error creating new conversation: ${e.toString()}");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF121212), // Global dark gray background
      appBar: AppBar(
        title: const Text("New Conversation"),
        elevation: 0,
        centerTitle: true,
        backgroundColor: const Color(0xFF1E1E1E),
        foregroundColor: Colors.white,
      ),
      drawer: const SideDrawer(),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 600),
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  "Ready when you are",
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 32),
                TextField(
                  controller: _messageController,
                  style: const TextStyle(
                    color: Colors.white,
                  ), // Input text color
                  decoration: InputDecoration(
                    filled: true,
                    fillColor: const Color(
                      0xFF1E1E1E,
                    ), // Dark input background matching cards
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 16,
                    ),
                    labelText: "Let's start the conversation!",
                    labelStyle: const TextStyle(
                      color: Colors.grey,
                      fontSize: 14,
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(
                        color: Colors.transparent,
                        width: 1,
                      ),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(
                        color: Colors.white,
                        width: 1.5,
                      ),
                    ),
                    suffixIcon: Padding(
                      padding: const EdgeInsets.only(right: 8.0),
                      child: IconButton(
                        onPressed: () => _handleSendMessage(),
                        icon: const Icon(
                          Icons.send,
                          color: Colors.white,
                        ), // Matching action accent color
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

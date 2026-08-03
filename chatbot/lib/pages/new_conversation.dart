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
      appBar: AppBar(title: Text("New Conversation")),
      drawer: SideDrawer(),
      body: Center(
        child: Container(
          margin: EdgeInsets.all(10),
          padding: EdgeInsets.all(10),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                "Ready when you are",
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),

              SizedBox(height: 30),
              Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(10),
                ),
                child: TextField(
                  controller: _messageController,
                  decoration: InputDecoration(
                    filled: true,
                    fillColor: Colors.white,
                    contentPadding: EdgeInsets.all(15),
                    hintText: "Let's start the conversation!",
                    hintStyle: TextStyle(
                      color: Color(0xffDDDADA),
                      fontSize: 14,
                    ),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    suffixIcon: Padding(
                      padding: const EdgeInsets.only(right: 8.0),
                      child: IconButton(
                        onPressed: () => _handleSendMessage(),
                        icon: const Icon(Icons.send),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

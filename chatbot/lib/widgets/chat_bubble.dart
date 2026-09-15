import 'package:flutter/material.dart';
import 'package:gpt_markdown/gpt_markdown.dart';

class ChatBubble extends StatelessWidget {
  final bool isUser;
  final String content;

  const ChatBubble({super.key, required this.isUser, required this.content});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: Color(0xFF2C2C2C),
          borderRadius: BorderRadius.circular(12).copyWith(
            bottomRight: isUser ? Radius.zero : const Radius.circular(12),
            bottomLeft: isUser ? const Radius.circular(12) : Radius.zero,
          ),
        ),
        child: isUser
            // user messages are plain, skip markdown parsing entirely
            ? SelectionArea(
                child: Text(
                  content,
                  style: const TextStyle(color: Colors.white),
                ),
              )
            : SelectionArea(
                child: GptMarkdown(
                  content,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                ),
              ),
      ),
    );
  }
}

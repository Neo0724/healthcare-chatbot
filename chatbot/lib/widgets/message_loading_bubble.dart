import 'package:flutter/material.dart';

class MessageLoadingBubble extends StatelessWidget {
  const MessageLoadingBubble({super.key});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: Color(0xFF2C2C2C),
          borderRadius: BorderRadius.circular(12).copyWith(
            bottomRight: const Radius.circular(12),
            bottomLeft: Radius.zero,
          ),
        ),

        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text("Generating response", style: TextStyle(color: Colors.grey)),
            SizedBox(width: 10),
            SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

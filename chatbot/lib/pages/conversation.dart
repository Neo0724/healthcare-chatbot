import 'package:chatbot/utils/socket_service.dart';
import 'package:chatbot/widgets/chat_bubble.dart';
import 'package:chatbot/widgets/side_drawer.dart';
import 'package:chatbot/models/message_history_model.dart';
import 'package:chatbot/utils/custom_dio.dart';
import 'package:flutter/material.dart';

class Conversation extends StatefulWidget {
  final String conversationId;
  bool redirectFromNew = false;
  Conversation({
    super.key,
    required this.conversationId,
    this.redirectFromNew = false,
  });

  @override
  State<Conversation> createState() => _ConversationState();
}

class _ConversationState extends State<Conversation> {
  List<MessageHistoryModel> _messageHistoryModel = [];
  List<MessageHistoryModel> _newMessages = [];
  bool redirectFromNew = false;

  final SocketService socketService = SocketService();
  late final ScrollController _scrollController;

  final _messageController = TextEditingController();
  Future<void> _getMessageAndResumeGraph() async {
    final response = await CustomDio.getCustomDio().get(
      "/get_conversation_message/${widget.conversationId}",
    );
    if (response.data["success"]) {
      final List<dynamic> rawList = response.data["message"];

      final List<MessageHistoryModel> converted = _messageHistoryModel = rawList
          .map((json) => MessageHistoryModel.fromJson(json))
          .toList();

      setState(() {
        _messageHistoryModel = converted;
      });

      if (rawList.length == 1) {
        _resumeGraph(converted[0].content);
      }

      _scrollController.jumpTo(_scrollController.position.maxScrollExtent);
    }
  }

  Future<void> _resumeGraph(String userMessage) async {
    if (!redirectFromNew) {
      setState(() {
        _newMessages.add(
          MessageHistoryModel(
            id: "temp_${DateTime.now().toString()}",
            messageType: MessageType.human,
            content: userMessage,
            createdAt: DateTime.now(),
          ),
        );
      });
    }

    redirectFromNew = false;

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.jumpTo(_scrollController.position.maxScrollExtent);
      }
    });

    await CustomDio.getCustomDio().post(
      "/resume/${widget.conversationId}",
      data: {"user_response": userMessage},
    );
  }

  Future<void> _handleReceiveMessage(dynamic data) async {
    final String receivedMessageId = data["id"];
    final String receivedMessage = data["content"];

    if (!_newMessages.any((msg) => msg.id == receivedMessageId)) {
      setState(() {
        _newMessages.add(
          MessageHistoryModel(
            id: receivedMessageId,
            messageType: MessageType.ai,
            content: receivedMessage,
            createdAt: DateTime.now(),
          ),
        );
      });
    } else {
      final index = _newMessages.indexWhere(
        (msg) => msg.id == receivedMessageId,
      );

      if (index != -1) {
        // Replace the old item with a new one
        setState(() {
          _newMessages[index] = _newMessages[index].copyWith(
            content: _newMessages[index].content + receivedMessage,
          );
        });
      }
    }

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients &&
          _scrollController.offset <
              _scrollController.position.maxScrollExtent - 200) {
        _scrollController.jumpTo(_scrollController.position.maxScrollExtent);
      }
    });
  }

  Future<void> _handleSendMessage() async {
    final String newMessage = _messageController.text;

    _resumeGraph(newMessage);

    _messageController.text = "";
  }

  @override
  void didUpdateWidget(covariant Conversation oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (oldWidget.conversationId != widget.conversationId) {
      setState(() {
        _messageController.text = "";
        _messageHistoryModel.clear();
        _newMessages.clear();
      });
      socketService.disconnect();
      socketService.connect(widget.conversationId, _handleReceiveMessage);
      _getMessageAndResumeGraph();
    }
  }

  @override
  void initState() {
    super.initState();
    redirectFromNew = widget.redirectFromNew;
    socketService.connect(widget.conversationId, _handleReceiveMessage);
    _getMessageAndResumeGraph();
    _scrollController = ScrollController();
  }

  @override
  void dispose() {
    super.dispose();
    socketService.disconnect();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Conversation")),
      drawer: SideDrawer(conversationId: widget.conversationId),
      body: Column(
        children: [
          _displayMessage([..._messageHistoryModel, ..._newMessages]),
          Padding(
            padding: const EdgeInsets.only(bottom: 20, left: 10, right: 10),
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
              ),
              child: TextField(
                controller: _messageController,
                decoration: InputDecoration(
                  filled: true,
                  fillColor: Colors.white,
                  contentPadding: EdgeInsets.all(15),
                  hintText: "Sends a message",
                  hintStyle: TextStyle(color: Color(0xffDDDADA), fontSize: 14),
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
          ),
        ],
      ),
    );
  }

  Expanded _displayMessage(List<MessageHistoryModel> messages) {
    return Expanded(
      child: ListView.builder(
        controller: _scrollController,
        padding: const EdgeInsets.all(12),
        itemCount: messages.length,
        itemBuilder: (context, index) {
          final message = messages[index];
          final isUser = message.messageType.name == "human";

          return SingleChildScrollView(
            key: ValueKey(message.id),
            child: ChatBubble(isUser: isUser, content: message.content),
          );
        },
      ),
    );
  }
}

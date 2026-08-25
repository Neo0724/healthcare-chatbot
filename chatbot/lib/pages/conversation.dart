import 'package:chatbot/utils/socket_service.dart';
import 'package:chatbot/widgets/chat_bubble.dart';
import 'package:chatbot/widgets/message_loading_bubble.dart';
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
  bool _isLoading = false;

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

    setState(() {
      _isLoading = true;
    });

    await CustomDio.getCustomDio().post(
      "/resume/${widget.conversationId}",
      data: {"user_response": userMessage},
    );
  }

  Future<void> _handleReceiveMessage(dynamic data) async {
    final String receivedMessageId = data["id"];
    final String receivedMessage = data["content"];
    final bool isLast = data["is_last"] is bool
        ? data["is_last"]
        : data["is_last"]?.toString().toLowerCase() == "true";

    if (isLast) {
      setState(() {
        _isLoading = false;
      });
    }

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

    if (newMessage.trim().isEmpty) {
      return;
    }

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
      appBar: AppBar(
        title: Text(
          "Conversation",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        elevation: 0,
        centerTitle: true,
        backgroundColor: const Color(0xFF1E1E1E),
        foregroundColor: Colors.white,
      ),
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
                style: const TextStyle(color: Colors.white), // Input text color
                decoration: InputDecoration(
                  filled: true,
                  fillColor: const Color(
                    0xFF1E1E1E,
                  ), // Dark input background matching cards
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 16,
                  ),
                  labelText: "Sends a message",
                  labelStyle: const TextStyle(color: Colors.grey, fontSize: 14),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: Colors.transparent, width: 1),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(
                      color: Colors.grey,
                      width: 1.5,
                    ),
                  ),
                  suffixIcon: Padding(
                    padding: EdgeInsets.only(right: 8.0),
                    child: IconButton(
                      onPressed: _isLoading ? null : () => _handleSendMessage(),
                      icon: Icon(
                        Icons.send,
                        color: _isLoading ? Colors.grey : Colors.white,
                      ), // Matching action accent color
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
        itemCount: _isLoading ? messages.length + 1 : messages.length,
        itemBuilder: (context, index) {
          // Display loading bubble when there is a pending message
          if (index == messages.length && _isLoading) {
            return const MessageLoadingBubble(); // Your simple loading bubble
          }

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

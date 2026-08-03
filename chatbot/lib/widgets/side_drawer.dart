import 'package:chatbot/models/conversation_history_model.dart';
import 'package:chatbot/router/app_router.dart';
import 'package:chatbot/states/auth_state.dart';
import 'package:chatbot/utils/custom_dio.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:go_router/go_router.dart';

enum ConversationPopupOption { delete }

class SideDrawer extends StatefulWidget {
  final String? conversationId;
  const SideDrawer({super.key, this.conversationId});

  @override
  State<SideDrawer> createState() => _SideDrawerState();
}

class _SideDrawerState extends State<SideDrawer> {
  String? _username;
  List<ConversationHistoryModel> _conversationHistoryModel = [];

  @override
  void initState() {
    super.initState();
    _loadUsername();
    _loadConversationHistory();
  }

  Future<void> _loadUsername() async {
    if (AuthState.isLoggedIn) {
      final storage = FlutterSecureStorage();

      final String? username = await storage.read(key: "username");

      if (!mounted) return;

      setState(() {
        _username = username;
      });
    }
  }

  Future<void> _loadConversationHistory() async {
    if (AuthState.isLoggedIn) {
      final response = await CustomDio.getCustomDio().get(
        "/get_conversation_history",
      );

      final List<dynamic> rawList = response.data["conversation_history"];

      setState(() {
        _conversationHistoryModel = rawList
            .map((json) => ConversationHistoryModel.fromJson(json))
            .toList();
      });
    }
  }

  Future<void> _handleLogout() async {
    try {
      final response = await CustomDio.getCustomDio().post("/auth/logout");
      if (response.data["success"] && response.statusCode == 200) {
        AuthState.logout();
        appRouter.goNamed("login");
      }
    } on DioException catch (err) {
      debugPrint("Login Error: ${err.toString()}");
    }
  }

  Padding _logoutBtn() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: SizedBox(
        width: double.infinity,
        height: 40,
        child: GestureDetector(
          onTap: () => _handleLogout(),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.lightBlue,
              borderRadius: BorderRadius.circular(7),
            ),
            child: const Center(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    "Logout",
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  SizedBox(width: 8),
                  Icon(Icons.logout_outlined, color: Colors.white),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Padding _loginBtn() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: SizedBox(
        width: double.infinity,
        height: 40,
        child: GestureDetector(
          onTap: () => context.goNamed('login'),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.lightBlue,
              borderRadius: BorderRadius.circular(7),
            ),
            child: const Center(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    "Login",
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  SizedBox(width: 8),
                  Icon(Icons.login_outlined, color: Colors.white),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _confirmDeleteDialog(BuildContext context, String conversationId) {
    bool onSameConversation = conversationId == widget.conversationId;
    showDialog(
      context: context,
      builder: (_) {
        return AlertDialog(
          title: Text("Confirm Deletion"),
          content: SizedBox(
            width: 250,
            height: 100,
            child: Text(
              "Are you sure you want to delete selected conversation?",
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancel"),
            ),
            FilledButton(
              onPressed: () async {
                try {
                  final response = await CustomDio.getCustomDio().delete(
                    "/delete_conversation/$conversationId",
                  );

                  debugPrint(response.toString());

                  if (!context.mounted) return;

                  if (response.statusCode == 200 && response.data["success"]) {
                    // Pop off alert dialog
                    Navigator.pop(context);

                    // Close drawer
                    Scaffold.of(context).closeDrawer();

                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: const Text('Deleted Successfully!'),
                          duration: const Duration(seconds: 2),
                          behavior: SnackBarBehavior.floating,
                          width: 300,
                          shape: RoundedRectangleBorder(
                            borderRadius: .circular(10.0),
                          ),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 15.0,
                            vertical: 10.0,
                          ),
                          action: SnackBarAction(label: 'OK', onPressed: () {}),
                        ),
                      );

                      if (onSameConversation) {
                        appRouter.go("/");
                      }
                    }
                  }
                } on DioException catch (err) {
                  debugPrint("Error deleting conversation: ${err.toString()}");
                }
              },
              child: const Text("Confirm Delete"),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: Column(
        children: [
          if (!AuthState.isLoggedIn)
            Expanded(
              child: Center(
                child: Text(
                  "Please login to view conversation histories",
                  textAlign: TextAlign.center,
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
              ),
            ),

          if (AuthState.isLoggedIn)
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: SizedBox(
                width: double.infinity,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      "Welcome back, $_username!",
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.settings),
                      onPressed: () {
                        // Navigate to settings page
                        context.goNamed('profile');
                      },
                    ),
                  ],
                ),
              ),
            ),

          if (AuthState.isLoggedIn)
            // Conversation Histories
            Expanded(
              child: ListView(
                padding: EdgeInsets.zero,
                children: [
                  ..._conversationHistoryModel.map((conversation) {
                    return Padding(
                      padding: const EdgeInsets.only(
                        left: 10,
                        right: 10,
                        bottom: 10,
                      ),
                      child: ListTile(
                        titleAlignment: ListTileTitleAlignment.center,
                        tileColor: Colors.cyan,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(7),
                        ),
                        title: Text(
                          conversation.title,
                          style: const TextStyle(color: Colors.white),
                        ),
                        onTap: () {
                          appRouter.goNamed(
                            "conversation",
                            pathParameters: {'id': conversation.id},
                            queryParameters: {"redirectFromNew": "false"},
                          );
                          Navigator.pop(context);
                        },
                        trailing: Transform.translate(
                          offset: const Offset(17, 0),
                          child: PopupMenuButton<ConversationPopupOption>(
                            onSelected: (ConversationPopupOption? value) {
                              if (value == ConversationPopupOption.delete) {
                                _confirmDeleteDialog(context, conversation.id);
                              }
                            },
                            itemBuilder: (BuildContext context) =>
                                <PopupMenuEntry<ConversationPopupOption>>[
                                  const PopupMenuItem<ConversationPopupOption>(
                                    value: ConversationPopupOption.delete,
                                    child: Row(
                                      children: [
                                        Icon(Icons.delete),
                                        SizedBox(width: 10),
                                        Text("Delete"),
                                      ],
                                    ),
                                  ),
                                ],
                          ),
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),

          // Logout button
          if (AuthState.isLoggedIn) _logoutBtn(),

          if (!AuthState.isLoggedIn) _loginBtn(),
        ],
      ),
    );
  }
}

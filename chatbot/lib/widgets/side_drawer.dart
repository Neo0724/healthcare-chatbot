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

  Widget _logoutBtn() {
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: GestureDetector(
        onTap: () => _handleLogout(),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white, // Dark text for contrast
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Center(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  "Logout",
                  style: TextStyle(
                    color: Color(0xFF121212), // Dark text for contrast
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                SizedBox(width: 8),
                Icon(Icons.logout_outlined, color: Colors.black),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _loginBtn() {
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: GestureDetector(
        onTap: () => context.goNamed('login'),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white, // Dark text for contrast
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Center(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  "Login",
                  style: TextStyle(
                    color: Color(0xFF121212), // Dark text for contrast
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                SizedBox(width: 8),
                Icon(Icons.login_outlined, color: Colors.black),
              ],
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
          backgroundColor: const Color(0xFF121212),
          title: Text(
            "Confirm Deletion",
            style: TextStyle(color: Colors.white),
          ),
          content: SizedBox(
            width: 250,
            height: 50,
            child: Text(
              "Are you sure you want to delete selected conversation?",
              style: TextStyle(color: Colors.white),
            ),
          ),
          actions: [
            TextButton(
              style: ButtonStyle(
                backgroundColor: WidgetStatePropertyAll(Color(0xFF2C2C2C)),
              ),
              onPressed: () => Navigator.pop(context),
              child: const Text(
                "Cancel",
                style: TextStyle(color: Colors.white),
              ),
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
              style: ButtonStyle(
                backgroundColor: WidgetStateProperty.all(Colors.white),
              ),
              child: const Text(
                "Confirm Delete",
                style: TextStyle(
                  color: Colors.black,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: const Color(0xFF121212), // Dark mode drawer background
      child: Column(
        children: [
          if (!AuthState.isLoggedIn)
            Expanded(
              child: Center(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0),
                  child: Text(
                    "Please login to view conversation histories",
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: Colors.grey[400],
                    ),
                  ),
                ),
              ),
            ),

          if (AuthState.isLoggedIn)
            Padding(
              padding: const EdgeInsets.fromLTRB(
                16,
                48,
                16,
                16,
              ), // Extra top spacing for status bar
              child: SizedBox(
                width: double.infinity,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      "Welcome back, $_username!",
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.settings, color: Colors.white70),
                      onPressed: () {
                        // Navigate to settings page
                        context.pushNamed('profile');
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
                  // Tile to create new conversation
                  Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 5,
                    ),
                    child: ListTile(
                      titleAlignment: ListTileTitleAlignment.center,
                      tileColor: Colors.white, // Matches your dark card color
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      title: Text(
                        "Create New Conversation",
                        style: const TextStyle(color: Colors.black),
                      ),
                      onTap: () {
                        appRouter.go("/");
                        Navigator.pop(context);
                      },
                      trailing: Transform.translate(
                        offset: const Offset(17, 0),
                        child: Icon(Icons.create_sharp, color: Colors.black),
                      ),
                    ),
                  ),
                  ..._conversationHistoryModel.map((conversation) {
                    return Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 5,
                      ),
                      child: ListTile(
                        titleAlignment: ListTileTitleAlignment.center,
                        tileColor: Color(
                          widget.conversationId == conversation.id
                              ? 0xFFFFFFFF
                              : 0xFF1E1E1E,
                        ), // Matches your dark card color
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        title: Text(
                          conversation.title,
                          style: TextStyle(
                            color: widget.conversationId == conversation.id
                                ? Colors.black
                                : Colors.white,
                          ),
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
                            color: const Color(
                              0xFF2C2C2C,
                            ), // Dark dropdown menu background
                            icon: const Icon(
                              Icons.more_vert,
                              color: Colors.grey,
                            ),
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
                                        Icon(
                                          Icons.delete,
                                          color: Colors.redAccent,
                                        ),
                                        SizedBox(width: 10),
                                        Text(
                                          "Delete",
                                          style: TextStyle(
                                            color: Colors.white70,
                                          ),
                                        ),
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
          if (AuthState.isLoggedIn)
            Padding(padding: const EdgeInsets.all(16.0), child: _logoutBtn()),

          if (!AuthState.isLoggedIn)
            Padding(padding: const EdgeInsets.all(16.0), child: _loginBtn()),
        ],
      ),
    );
  }
}

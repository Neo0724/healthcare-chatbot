import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthState extends ChangeNotifier {
  static bool _isLoggedIn = false;

  static Future<void> initialize() async {
    final storage = FlutterSecureStorage();

    final String? token = await storage.read(key: "access_token");

    if (token == null) {
      _isLoggedIn = false;
    } else {
      _isLoggedIn = true;
    }
  }

  static bool get isLoggedIn => _isLoggedIn;

  static void login() {
    _isLoggedIn = true;
  }

  static void logout() {
    _isLoggedIn = false;
  }
}

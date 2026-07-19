import 'package:flutter/material.dart';

class AuthState extends ChangeNotifier {
  static bool _isLoggedIn = false;

  bool get isLoggedIn => _isLoggedIn;

  static void login() {
    _isLoggedIn = true;
  }

  static void logout() {
    _isLoggedIn = false;
  }
}

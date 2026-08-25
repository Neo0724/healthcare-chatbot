import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthState extends ChangeNotifier {
  // Private constructor
  AuthState._internal();

  // Static singleton instance
  static final AuthState instance = AuthState._internal();

  // Factory constructor returning the singleton instance
  factory AuthState() => instance;

  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  bool _isLoggedIn = false;

  bool get isLoggedIn => _isLoggedIn;

  Future<void> initialize() async {
    final String? token = await _storage.read(key: "access_token");

    _isLoggedIn = token != null && token.isNotEmpty;
    notifyListeners();
  }

  Future<void> login(
    String accessToken,
    String refreshToken,
    String username,
  ) async {
    await _storage.write(key: "access_token", value: accessToken);
    await _storage.write(key: "refresh_token", value: refreshToken);
    await _storage.write(key: "username", value: username);
    _isLoggedIn = true;
    notifyListeners();
  }

  Future<void> logout() async {
    await _storage.delete(key: "access_token");
    await _storage.delete(key: "refresh_token");
    await _storage.delete(key: "username");
    _isLoggedIn = false;
    notifyListeners();
  }
}

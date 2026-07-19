import 'package:chatbot/router/app_router.dart';
import 'package:chatbot/states/auth_state.dart';
import 'package:dio/dio.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class CustomDio {
  final Dio _customDio = Dio();
  final storage = FlutterSecureStorage();

  CustomDio() {
    _customDio.options.baseUrl = dotenv.get("API_URL");
    _customDio.options.connectTimeout = Duration(seconds: 5);
    _customDio.options.receiveTimeout = Duration(seconds: 5);

    _customDio.interceptors.add(
      InterceptorsWrapper(
        onRequest:
            (RequestOptions options, RequestInterceptorHandler handler) async {
              final accessToken = await storage.read(key: "access_token");
              if (accessToken != null) {
                options.headers["Authorization"] = "Bearer $accessToken";
              }

              handler.next(options);
            },

        onError: (DioException error, ErrorInterceptorHandler handler) async {
          if (error.response?.statusCode != 401) {
            return handler.next(error);
          }

          final refreshToken = await storage.read(key: "refresh_token");

          if (refreshToken == null) {
            _handleLogout();

            return handler.reject(error);
          }

          final success = await _refreshAccessToken(refreshToken);

          if (!success) {
            _handleLogout();
            return handler.reject(error);
          }

          final accessToken = await storage.read(key: "access_token");
          error.requestOptions.headers["Authorization"] = "Bearer $accessToken";
          final response = await _customDio.fetch(error.requestOptions);
          return handler.resolve(response);
        },
      ),
    );
  }

  Future<bool> _refreshAccessToken(String refreshToken) async {
    try {
      final response = await Dio().post(
        "/auth/refresh_access_token",
        data: {"refresh_token": refreshToken},
      );

      if (response.statusCode == 200) {
        final newRefreshToken = response.data["refresh_token"];
        final newAccessToken = response.data["access_token"];

        await storage.write(key: "refresh_token", value: newRefreshToken);
        await storage.write(key: "access_token", value: newAccessToken);
        return true;
      } else {
        await storage.deleteAll();
        return false;
      }
    } catch (e) {
      debugPrint("Refresh Access Token Error : $e");
      return false;
    }
  }

  void _handleLogout() {
    if (appRouter.routerDelegate.currentConfiguration.uri.path != '/login') {
      appRouter.go("/login");
    }
    AuthState.logout();
  }
}

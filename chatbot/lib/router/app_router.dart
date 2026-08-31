import 'package:chatbot/pages/profile.dart';
import 'package:chatbot/pages/conversation.dart';
import 'package:chatbot/pages/login.dart';
import 'package:chatbot/pages/new_conversation.dart';
import 'package:chatbot/pages/register.dart';
import 'package:chatbot/states/auth_state.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:go_router/go_router.dart';

final protectedRoute = <String>['/', '/profile'];

final guestRoute = <String>['/login', '/register'];

final storage = FlutterSecureStorage();

final GoRouter appRouter = GoRouter(
  refreshListenable: AuthState.instance,
  redirect: (context, state) {
    final loggedIn = AuthState.instance.isLoggedIn;

    if (!loggedIn && protectedRoute.contains(state.matchedLocation)) {
      return "/login";
    }

    if (loggedIn && guestRoute.contains(state.matchedLocation)) {
      return '/';
    }

    return null;
  },
  initialLocation: '/',
  routes: <GoRoute>[
    GoRoute(path: '/', builder: (context, state) => const NewConversation()),
    GoRoute(
      path: '/conversation/:id',
      builder: (context, state) {
        final conversationId = state.pathParameters['id'] ?? "";
        final bool redirectFromNew =
            state.uri.queryParameters["redirectFromNew"]?.toLowerCase() ==
            "true";
        return Conversation(
          conversationId: conversationId,
          redirectFromNew: redirectFromNew,
        );
      },
      name: "conversation",
    ),
    GoRoute(
      path: '/login',
      builder: (context, state) => const Login(),
      name: 'login',
    ),
    GoRoute(
      path: '/register',
      builder: (context, state) => const Register(),
      name: 'register',
    ),
    GoRoute(
      path: '/profile',
      builder: (context, state) => Profile(),
      name: 'profile',
    ),
  ],
);

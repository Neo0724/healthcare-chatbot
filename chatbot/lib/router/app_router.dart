import 'package:chatbot/pages/first_page.dart';
import 'package:chatbot/pages/login.dart';
import 'package:chatbot/pages/new_conversation.dart';
import 'package:chatbot/pages/register.dart';
import 'package:chatbot/states/auth_state.dart';
import 'package:go_router/go_router.dart';

final authState = AuthState();
final protectedRoute = <String>['/first_page', '/profile'];

final guestRoute = <String>['/login', '/register'];

final GoRouter appRouter = GoRouter(
  refreshListenable: authState,
  redirect: (context, state) {
    final loggedIn = authState.isLoggedIn;

    if (!loggedIn && protectedRoute.contains(state.matchedLocation)) {
      return "/login";
    }

    if (loggedIn && guestRoute.contains(state.matchedLocation)) {
      return '/first_page';
    }

    return null;
  },
  initialLocation: '/login',
  routes: <GoRoute>[
    GoRoute(path: '/', builder: (context, state) => const NewConversation()),
    GoRoute(
      path: '/first_page',
      builder: (context, state) => const FirstPage(),
    ),
    GoRoute(path: '/login', builder: (context, state) => const Login()),
    GoRoute(path: '/register', builder: (context, state) => const Register()),
  ],
);

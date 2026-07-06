# Skill: Advanced State Management in Flutter

## Purpose
To implement robust, scalable state management in Flutter applications using Riverpod, Bloc, and Provider patterns.

## When to Use
- When building medium to large Flutter applications with complex state flows
- For managing shared state across multiple widgets and screens
- When you need predictable, testable state management
- For handling asynchronous operations (API calls, database queries) with state
- When you need to separate business logic from UI

## Procedure

### 1. Riverpod Setup
Modern, compile-safe state management.

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Define a provider
final counterProvider = StateProvider<int>((ref) => 0);

void main() {
  runApp(
    ProviderScope(
      child: MyApp(),
    ),
  );
}

class MyApp extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('Riverpod Counter')),
        body: Consumer(
          builder: (context, ref, child) {
            final count = ref.watch(counterProvider);
            return Center(child: Text('Count: $count'));
          },
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () => ref.read(counterProvider.notifier).state++,
          child: Icon(Icons.add),
        ),
      ),
    );
  }
}
```

### 2. Async Notifier for API Calls
Handle async operations with Riverpod.

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class Todo {
  final int id;
  final String title;
  final bool completed;

  Todo({required this.id, required this.title, required this.completed});

  factory Todo.fromJson(Map<String, dynamic> json) {
    return Todo(
      id: json['id'],
      title: json['title'],
      completed: json['completed'],
    );
  }
}

final todoListProvider = AsyncNotifierProvider<TodoListNotifier, List<Todo>>(
  TodoListNotifier.new,
);

class TodoListNotifier extends AsyncNotifier<List<Todo>> {
  @override
  Future<List<Todo>> build() async {
    final response = await http.get(Uri.parse('https://jsonplaceholder.typicode.com/todos'));
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Todo.fromJson(json)).toList();
    }
    throw Exception('Failed to load todos');
  }

  Future<void> addTodo(String title) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final response = await http.post(
        Uri.parse('https://jsonplaceholder.typicode.com/todos'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'title': title, 'completed': false}),
      );
      if (response.statusCode == 201) {
        final newTodo = Todo.fromJson(json.decode(response.body));
        return [...?state.value, newTodo];
      }
      throw Exception('Failed to add todo');
    });
  }
}
```

### 3. Bloc for Complex State Flows
Use Bloc for more complex state transitions.

```dart
import 'package:flutter_bloc/flutter_bloc.dart';

// Events
abstract class AuthEvent {}
class LoginRequested extends AuthEvent {
  final String email;
  final String password;
  LoginRequested({required this.email, required this.password});
}
class LogoutRequested extends AuthEvent {}

// States
abstract class AuthState {}
class AuthInitial extends AuthState {}
class AuthLoading extends AuthState {}
class AuthAuthenticated extends AuthState {
  final String token;
  AuthAuthenticated({required this.token});
}
class AuthError extends AuthState {
  final String message;
  AuthError({required this.message});
}

// Bloc
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  AuthBloc() : super(AuthInitial()) {
    on<LoginRequested>(_onLoginRequested);
    on<LogoutRequested>(_onLogoutRequested);
  }

  Future<void> _onLoginRequested(LoginRequested event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    try {
      // Simulate API call
      await Future.delayed(Duration(seconds: 2));
      emit(AuthAuthenticated(token: 'fake-jwt-token'));
    } catch (e) {
      emit(AuthError(message: 'Login failed: $e'));
    }
  }

  void _onLogoutRequested(LogoutRequested event, Emitter<AuthState> emit) {
    emit(AuthInitial());
  }
}
```

## Best Practices
- **Choose Wisely**: Use Provider for simple apps, Riverpod for medium, Bloc for complex
- **Immutability**: Always use immutable state objects
- **Separation of Concerns**: Keep business logic in providers/blocs, not widgets
- **Testing**: Write unit tests for your state management logic
- **Performance**: Use `select` in Riverpod to only rebuild widgets when needed
- **Error Handling**: Always handle errors gracefully and provide user feedback

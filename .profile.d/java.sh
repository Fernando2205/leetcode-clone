#!/usr/bin/env bash
JAVA_BIN="$(find /app/.apt/usr/lib/jvm -type f -name javac 2>/dev/null | head -n1)"
if [ -n "$JAVA_BIN" ]; then
  export JAVA_HOME="$(dirname "$(dirname "$JAVA_BIN")")"
  export PATH="$JAVA_HOME/bin:$PATH"
fi
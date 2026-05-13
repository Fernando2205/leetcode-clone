#!/usr/bin/env bash

# Prefer a real JDK home under /app/.apt/usr/lib/jvm to avoid broken JAVA_HOME
# values derived from symlinks like /app/.apt/usr/bin/javac.
JAVA_HOME_CANDIDATE="$(find /app/.apt/usr/lib/jvm -mindepth 1 -maxdepth 1 -type d 2>/dev/null | head -n1)"

if [ -n "$JAVA_HOME_CANDIDATE" ]; then
  if [ -f "$JAVA_HOME_CANDIDATE/conf/security/java.security" ] || [ -f "$JAVA_HOME_CANDIDATE/lib/security/java.security" ]; then
    export JAVA_HOME="$JAVA_HOME_CANDIDATE"
    export PATH="$JAVA_HOME/bin:/app/.apt/usr/bin:$PATH"
  fi
fi

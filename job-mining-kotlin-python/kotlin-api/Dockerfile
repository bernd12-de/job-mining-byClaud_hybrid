# Multi-stage build for Kotlin Spring Boot app
# Stage 1: build with Gradle
FROM gradle:8-jdk17 AS builder
WORKDIR /home/gradle/project
COPY --chown=gradle:gradle . /home/gradle/project
RUN ./gradlew clean build -x test --no-daemon

# Stage 2: runtime image
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /home/gradle/project/build/libs/*.jar /app/app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]

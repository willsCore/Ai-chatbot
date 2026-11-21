CREATE DATABASE IF NOT EXISTS ai_chatbot
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ai_chatbot;

-- Created User's Table
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50)  NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  
);

-- Created chat_history table
CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role ENUM('user','assistant') NOT NULL, -- ENUM restricts a column to only accept a predefined list of allowed string values.

    content TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_chat_history_user (user_id),-- INDEX idx_chat_history_user (user_id) creates a database lookup shortcut on the user_id column
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);



-- Created a logs table to keep track of user
CREATE TABLE IF NOT EXISTS logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  event_type VARCHAR(30) NOT NULL,
  path VARCHAR(100) NOT NULL,
  method VARCHAR(10) NOT NULL,
  status_code SMALLINT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_logs_user(user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
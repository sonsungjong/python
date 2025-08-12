-- SQL Shell (psql) 또는 pgAdmin4 실행 후

-- gen_random_uuid() 설치
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 사용자 정보 테이블 (사용자식별자, 유저아이디, 유저비밀번호, 유저이름, 유저이메일, 유저권한, 유저생성일자)
CREATE TABLE IF NOT EXISTS app_user (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
  user_id TEXT UNIQUE NOT NULL, 
  user_password TEXT, 
  user_name TEXT,
  user_email TEXT,
  user_auth INT NOT NULL DEFAULT 1, 
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 각 유저의 채팅방 테이블 (방식별자, 사용자식별자, 방제목, 방생성일자)
CREATE TABLE IF NOT EXISTS chat_room(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
  title TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 각 채팅방의 채팅 메시지 테이블 (채팅식별자, 방식별자, 사용자식별자, 채팅역할[system, assistant, ...])
CREATE TABLE IF NOT EXISTS chat_message(
  id BIGSERIAL PRIMARY KEY,
  room_id UUID NOT NULL REFERENCES chat_room(id) ON DELETE CASCADE,
  user_id UUID REFERENCES app_user(id) ON DELETE SET NULL,
  role TEXT,
  content TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 인덱싱
-- 유저별 채팅방 목록
CREATE INDEX IF NOT EXISTS idx_chat_room_owner ON chat_room(user_id, created_at);
-- 채팅방의 메시지 (시간순, 최신이 마지막)
CREATE INDEX IF NOT EXISTS idx_chat_msg_room ON chat_message(room_id, id);
-- 해당 유저의 모든 메시지 (시간순, 최신이 마지막)
CREATE INDEX IF NOT EXISTS idx_chat_msg_user ON chat_message(user_id, created_at);
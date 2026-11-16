-- Adminer 5.4.0 PostgreSQL 17.6 dump

DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS users_id_seq;
CREATE SEQUENCE users_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."users" (
    "id" integer DEFAULT nextval('users_id_seq') NOT NULL,
    "username" character varying(50) NOT NULL,
    "password_hash" text NOT NULL,
    "role" character varying(10) NOT NULL,
    "created_at" timestamp DEFAULT now(),
    CONSTRAINT "users_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "users_role_check" CHECK ((role)::text = ANY ((ARRAY['author'::character varying, 'editor'::character varying])::text[]))
)
WITH (oids = false);

CREATE UNIQUE INDEX users_username_key ON public.users USING btree (username);


-- 2026-11-16 14:26:23 UTC

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



-- Adminer 5.4.0 PostgreSQL 17.6 dump

DROP TABLE IF EXISTS "manuscripts";
DROP SEQUENCE IF EXISTS manuscripts_id_seq;
CREATE SEQUENCE manuscripts_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."manuscripts" (
    "id" integer DEFAULT nextval('manuscripts_id_seq') NOT NULL,
    "author_id" integer NOT NULL,
    "category" character varying(30) NOT NULL,
    "title" character varying(200) NOT NULL,
    "content" text NOT NULL,
    "status" character varying(10) DEFAULT 'draft' NOT NULL,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp,
    CONSTRAINT "manuscripts_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "manuscripts_status_check" CHECK ((status)::text = ANY ((ARRAY['draft'::character varying, 'review'::character varying, 'approved'::character varying])::text[]))
)
WITH (oids = false);


ALTER TABLE ONLY "public"."manuscripts" ADD CONSTRAINT "manuscripts_author_id_fkey" FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE NOT DEFERRABLE;

-- 2026-11-16 14:26:28 UTC

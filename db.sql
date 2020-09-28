--
-- PostgreSQL database dump
--

-- Dumped from database version 11.5
-- Dumped by pg_dump version 12.0

-- Started on 2020-04-08 03:40:42 MSK

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 595 (class 1247 OID 16512)
-- Name: account_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.account_type AS ENUM (
    'ALGO',
    'MANUAL'
);


SET default_tablespace = '';

--
-- TOC entry 196 (class 1259 OID 16477)
-- Name: snapshot24h; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.snapshot24h (
    dt timestamp without time zone NOT NULL,
    id bigint NOT NULL,
    asset character(6) NOT NULL,
    free numeric NOT NULL,
    locked numeric NOT NULL,
    usd numeric(10,2),
    btc numeric,
    account public.account_type NOT NULL
);


--
-- TOC entry 197 (class 1259 OID 16483)
-- Name: regular_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.regular_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3815 (class 0 OID 0)
-- Dependencies: 197
-- Name: regular_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.regular_id_seq OWNED BY public.snapshot24h.id;


--
-- TOC entry 3684 (class 2604 OID 16485)
-- Name: snapshot24h id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.snapshot24h ALTER COLUMN id SET DEFAULT nextval('public.regular_id_seq'::regclass);


--
-- TOC entry 3808 (class 0 OID 16477)
-- Dependencies: 196
-- Data for Name: snapshot24h; Type: TABLE DATA; Schema: public; Owner: -
--


--
-- TOC entry 3816 (class 0 OID 0)
-- Dependencies: 197
-- Name: regular_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.regular_id_seq', 2499, true);


--
-- TOC entry 3686 (class 2606 OID 16487)
-- Name: snapshot24h regular_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.snapshot24h
    ADD CONSTRAINT regular_pkey PRIMARY KEY (id);

--
-- PostgreSQL database dump complete
--


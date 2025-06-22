--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: anomaly; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.anomaly (
    anomaly_id character varying NOT NULL,
    image_path character varying NOT NULL,
    class_id integer NOT NULL,
    cl double precision NOT NULL,
    xcenter double precision NOT NULL,
    ycenter double precision NOT NULL,
    width double precision NOT NULL,
    height double precision NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.anomaly OWNER TO postgres;

--
-- Name: class; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.class (
    class_id integer NOT NULL,
    class_name character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.class OWNER TO postgres;

--
-- Name: class_defect_class_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.class_defect_class_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.class_defect_class_id_seq OWNER TO postgres;

--
-- Name: class_defect_class_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.class_defect_class_id_seq OWNED BY public.class.class_id;


--
-- Name: defect; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.defect (
    defect_id character varying NOT NULL,
    image_path character varying NOT NULL,
    class_id integer NOT NULL,
    cl double precision NOT NULL,
    xcenter double precision NOT NULL,
    ycenter double precision NOT NULL,
    width double precision NOT NULL,
    height double precision NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.defect OWNER TO postgres;

--
-- Name: final_defect; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.final_defect (
    final_id character varying NOT NULL,
    image_path character varying NOT NULL,
    source_id character varying NOT NULL,
    class_id integer NOT NULL,
    training_id integer,
    confidence_level double precision NOT NULL,
    xcenter double precision NOT NULL,
    ycenter double precision NOT NULL,
    width double precision NOT NULL,
    height double precision NOT NULL
);


ALTER TABLE public.final_defect OWNER TO postgres;

--
-- Name: operation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.operation (
    operation_id integer NOT NULL,
    start_time timestamp with time zone DEFAULT now() NOT NULL,
    end_time timestamp with time zone DEFAULT now() NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.operation OWNER TO postgres;

--
-- Name: operation_operation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.operation_operation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.operation_operation_id_seq OWNER TO postgres;

--
-- Name: operation_operation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.operation_operation_id_seq OWNED BY public.operation.operation_id;


--
-- Name: user_admin; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_admin (
    user_id integer NOT NULL,
    username character varying NOT NULL,
    password character varying NOT NULL,
    role character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_admin OWNER TO postgres;

--
-- Name: user_admin_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_admin_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_admin_user_id_seq OWNER TO postgres;

--
-- Name: user_admin_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_admin_user_id_seq OWNED BY public.user_admin.user_id;


--
-- Name: class class_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class ALTER COLUMN class_id SET DEFAULT nextval('public.class_defect_class_id_seq'::regclass);


--
-- Name: operation operation_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.operation ALTER COLUMN operation_id SET DEFAULT nextval('public.operation_operation_id_seq'::regclass);


--
-- Name: user_admin user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_admin ALTER COLUMN user_id SET DEFAULT nextval('public.user_admin_user_id_seq'::regclass);


--
-- Data for Name: anomaly; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.anomaly (anomaly_id, image_path, class_id, cl, xcenter, ycenter, width, height, created_at) FROM stdin;
\.


--
-- Data for Name: class; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.class (class_id, class_name, created_at) FROM stdin;
0	Anomaly	2025-06-21 16:00:48.02312+07
1	Dent	2025-06-21 13:00:15.548443+07
\.


--
-- Data for Name: defect; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.defect (defect_id, image_path, class_id, cl, xcenter, ycenter, width, height, created_at) FROM stdin;
\.


--
-- Data for Name: final_defect; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.final_defect (final_id, image_path, source_id, class_id, training_id, confidence_level, xcenter, ycenter, width, height) FROM stdin;
\.


--
-- Data for Name: operation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.operation (operation_id, start_time, end_time, user_id) FROM stdin;
\.


--
-- Data for Name: user_admin; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_admin (user_id, username, password, role, created_at) FROM stdin;
1	admin123	admin123	admin	2025-06-21 11:48:03.182257+07
\.


--
-- Name: class_defect_class_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.class_defect_class_id_seq', 2, true);


--
-- Name: operation_operation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.operation_operation_id_seq', 3, true);


--
-- Name: user_admin_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_admin_user_id_seq', 1, true);


--
-- Name: anomaly anomaly_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anomaly
    ADD CONSTRAINT anomaly_pkey PRIMARY KEY (anomaly_id);


--
-- Name: class class_defect_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class
    ADD CONSTRAINT class_defect_pkey PRIMARY KEY (class_id);


--
-- Name: defect defect_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.defect
    ADD CONSTRAINT defect_pkey PRIMARY KEY (defect_id);


--
-- Name: final_defect final_defect_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.final_defect
    ADD CONSTRAINT final_defect_pkey PRIMARY KEY (final_id);


--
-- Name: operation operation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.operation
    ADD CONSTRAINT operation_pkey PRIMARY KEY (operation_id);


--
-- Name: user_admin user_admin_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_admin
    ADD CONSTRAINT user_admin_pkey PRIMARY KEY (user_id);


--
-- Name: anomaly class_anomaly; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anomaly
    ADD CONSTRAINT class_anomaly FOREIGN KEY (class_id) REFERENCES public.class(class_id);


--
-- Name: defect class_defect; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.defect
    ADD CONSTRAINT class_defect FOREIGN KEY (class_id) REFERENCES public.class(class_id);


--
-- Name: final_defect class_final; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.final_defect
    ADD CONSTRAINT class_final FOREIGN KEY (class_id) REFERENCES public.class(class_id);


--
-- Name: operation user_operation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.operation
    ADD CONSTRAINT user_operation FOREIGN KEY (user_id) REFERENCES public.user_admin(user_id) NOT VALID;


--
-- PostgreSQL database dump complete
--


PGDMP  !    #                }            vet_clinica_pSQL    17.4    17.4 -    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false            �           1262    33428    vet_clinica_pSQL    DATABASE     x   CREATE DATABASE "vet_clinica_pSQL" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'ru-RU';
 "   DROP DATABASE "vet_clinica_pSQL";
                     postgres    false            �            1259    33528    Журнал_входа    TABLE     X  CREATE TABLE public."Журнал_входа" (
    id integer NOT NULL,
    user_id integer NOT NULL,
    datetime timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    event_type text NOT NULL,
    CONSTRAINT "Журнал_входа_event_type_check" CHECK ((event_type = ANY (ARRAY['вход'::text, 'выход'::text])))
);
 -   DROP TABLE public."Журнал_входа";
       public         heap r       postgres    false            �            1259    33527    Журнал_входа_id_seq    SEQUENCE     �   CREATE SEQUENCE public."Журнал_входа_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public."Журнал_входа_id_seq";
       public               postgres    false    226            �           0    0    Журнал_входа_id_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public."Журнал_входа_id_seq" OWNED BY public."Журнал_входа".id;
          public               postgres    false    225            �            1259    33506    Приёмы    TABLE     �  CREATE TABLE public."Приёмы" (
    id integer NOT NULL,
    animal_id text NOT NULL,
    vet_id integer NOT NULL,
    date date NOT NULL,
    "time" time without time zone NOT NULL,
    service_id integer NOT NULL,
    status text NOT NULL,
    CONSTRAINT "Приёмы_status_check" CHECK ((status = ANY (ARRAY['запланирован'::text, 'завершен'::text, 'отменен'::text])))
);
 "   DROP TABLE public."Приёмы";
       public         heap r       postgres    false            �            1259    33505    Приёмы_id_seq    SEQUENCE     �   CREATE SEQUENCE public."Приёмы_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public."Приёмы_id_seq";
       public               postgres    false    224            �           0    0    Приёмы_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public."Приёмы_id_seq" OWNED BY public."Приёмы".id;
          public               postgres    false    223            �            1259    33480    Сотрудники    TABLE     �   CREATE TABLE public."Сотрудники" (
    id integer NOT NULL,
    full_name text NOT NULL,
    login text NOT NULL,
    password_hash text NOT NULL,
    role text NOT NULL,
    branch_id integer NOT NULL
);
 *   DROP TABLE public."Сотрудники";
       public         heap r       postgres    false            �            1259    33479    Сотрудники_id_seq    SEQUENCE     �   CREATE SEQUENCE public."Сотрудники_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public."Сотрудники_id_seq";
       public               postgres    false    220            �           0    0    Сотрудники_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public."Сотрудники_id_seq" OWNED BY public."Сотрудники".id;
          public               postgres    false    219            �            1259    33496    Услуги    TABLE     �   CREATE TABLE public."Услуги" (
    id integer NOT NULL,
    title text NOT NULL,
    description text,
    price numeric(10,2) NOT NULL,
    CONSTRAINT "Услуги_price_check" CHECK ((price >= (0)::numeric))
);
 "   DROP TABLE public."Услуги";
       public         heap r       postgres    false            �            1259    33495    Услуги_id_seq    SEQUENCE     �   CREATE SEQUENCE public."Услуги_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public."Услуги_id_seq";
       public               postgres    false    222            �           0    0    Услуги_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public."Услуги_id_seq" OWNED BY public."Услуги".id;
          public               postgres    false    221            �            1259    33471    Филиалы    TABLE     �   CREATE TABLE public."Филиалы" (
    id integer NOT NULL,
    name text NOT NULL,
    address text NOT NULL,
    phone text NOT NULL
);
 $   DROP TABLE public."Филиалы";
       public         heap r       postgres    false            �            1259    33470    Филиалы_id_seq    SEQUENCE     �   CREATE SEQUENCE public."Филиалы_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public."Филиалы_id_seq";
       public               postgres    false    218            �           0    0    Филиалы_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public."Филиалы_id_seq" OWNED BY public."Филиалы".id;
          public               postgres    false    217            9           2604    33531    Журнал_входа id    DEFAULT     �   ALTER TABLE ONLY public."Журнал_входа" ALTER COLUMN id SET DEFAULT nextval('public."Журнал_входа_id_seq"'::regclass);
 K   ALTER TABLE public."Журнал_входа" ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    226    225    226            8           2604    33509    Приёмы id    DEFAULT     v   ALTER TABLE ONLY public."Приёмы" ALTER COLUMN id SET DEFAULT nextval('public."Приёмы_id_seq"'::regclass);
 @   ALTER TABLE public."Приёмы" ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    223    224    224            6           2604    33483    Сотрудники id    DEFAULT     �   ALTER TABLE ONLY public."Сотрудники" ALTER COLUMN id SET DEFAULT nextval('public."Сотрудники_id_seq"'::regclass);
 H   ALTER TABLE public."Сотрудники" ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    220    219    220            7           2604    33499    Услуги id    DEFAULT     v   ALTER TABLE ONLY public."Услуги" ALTER COLUMN id SET DEFAULT nextval('public."Услуги_id_seq"'::regclass);
 @   ALTER TABLE public."Услуги" ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    222    221    222            5           2604    33474    Филиалы id    DEFAULT     z   ALTER TABLE ONLY public."Филиалы" ALTER COLUMN id SET DEFAULT nextval('public."Филиалы_id_seq"'::regclass);
 B   ALTER TABLE public."Филиалы" ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    217    218    218            �          0    33528    Журнал_входа 
   TABLE DATA           V   COPY public."Журнал_входа" (id, user_id, datetime, event_type) FROM stdin;
    public               postgres    false    226   :       �          0    33506    Приёмы 
   TABLE DATA           a   COPY public."Приёмы" (id, animal_id, vet_id, date, "time", service_id, status) FROM stdin;
    public               postgres    false    224   �:       �          0    33480    Сотрудники 
   TABLE DATA           f   COPY public."Сотрудники" (id, full_name, login, password_hash, role, branch_id) FROM stdin;
    public               postgres    false    220   �;       �          0    33496    Услуги 
   TABLE DATA           G   COPY public."Услуги" (id, title, description, price) FROM stdin;
    public               postgres    false    222   �<       �          0    33471    Филиалы 
   TABLE DATA           D   COPY public."Филиалы" (id, name, address, phone) FROM stdin;
    public               postgres    false    218   �=       �           0    0    Журнал_входа_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public."Журнал_входа_id_seq"', 6, true);
          public               postgres    false    225            �           0    0    Приёмы_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public."Приёмы_id_seq"', 5, true);
          public               postgres    false    223            �           0    0    Сотрудники_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public."Сотрудники_id_seq"', 9, true);
          public               postgres    false    219            �           0    0    Услуги_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public."Услуги_id_seq"', 5, true);
          public               postgres    false    221            �           0    0    Филиалы_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public."Филиалы_id_seq"', 4, true);
          public               postgres    false    217            G           2606    33516    Приёмы unique_appointment 
   CONSTRAINT     l   ALTER TABLE ONLY public."Приёмы"
    ADD CONSTRAINT unique_appointment UNIQUE (vet_id, date, "time");
 K   ALTER TABLE ONLY public."Приёмы" DROP CONSTRAINT unique_appointment;
       public                 postgres    false    224    224    224            K           2606    33537 4   Журнал_входа Журнал_входа_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public."Журнал_входа"
    ADD CONSTRAINT "Журнал_входа_pkey" PRIMARY KEY (id);
 b   ALTER TABLE ONLY public."Журнал_входа" DROP CONSTRAINT "Журнал_входа_pkey";
       public                 postgres    false    226            I           2606    33514    Приёмы Приёмы_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public."Приёмы"
    ADD CONSTRAINT "Приёмы_pkey" PRIMARY KEY (id);
 L   ALTER TABLE ONLY public."Приёмы" DROP CONSTRAINT "Приёмы_pkey";
       public                 postgres    false    224            A           2606    33489 3   Сотрудники Сотрудники_login_key 
   CONSTRAINT     s   ALTER TABLE ONLY public."Сотрудники"
    ADD CONSTRAINT "Сотрудники_login_key" UNIQUE (login);
 a   ALTER TABLE ONLY public."Сотрудники" DROP CONSTRAINT "Сотрудники_login_key";
       public                 postgres    false    220            C           2606    33487 .   Сотрудники Сотрудники_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public."Сотрудники"
    ADD CONSTRAINT "Сотрудники_pkey" PRIMARY KEY (id);
 \   ALTER TABLE ONLY public."Сотрудники" DROP CONSTRAINT "Сотрудники_pkey";
       public                 postgres    false    220            E           2606    33504    Услуги Услуги_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public."Услуги"
    ADD CONSTRAINT "Услуги_pkey" PRIMARY KEY (id);
 L   ALTER TABLE ONLY public."Услуги" DROP CONSTRAINT "Услуги_pkey";
       public                 postgres    false    222            ?           2606    33478 "   Филиалы Филиалы_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public."Филиалы"
    ADD CONSTRAINT "Филиалы_pkey" PRIMARY KEY (id);
 P   ALTER TABLE ONLY public."Филиалы" DROP CONSTRAINT "Филиалы_pkey";
       public                 postgres    false    218            O           2606    33538 <   Журнал_входа Журнал_входа_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public."Журнал_входа"
    ADD CONSTRAINT "Журнал_входа_user_id_fkey" FOREIGN KEY (user_id) REFERENCES public."Сотрудники"(id) ON DELETE CASCADE;
 j   ALTER TABLE ONLY public."Журнал_входа" DROP CONSTRAINT "Журнал_входа_user_id_fkey";
       public               postgres    false    4675    226    220            M           2606    33522 )   Приёмы Приёмы_service_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public."Приёмы"
    ADD CONSTRAINT "Приёмы_service_id_fkey" FOREIGN KEY (service_id) REFERENCES public."Услуги"(id) ON DELETE RESTRICT;
 W   ALTER TABLE ONLY public."Приёмы" DROP CONSTRAINT "Приёмы_service_id_fkey";
       public               postgres    false    224    4677    222            N           2606    33517 %   Приёмы Приёмы_vet_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public."Приёмы"
    ADD CONSTRAINT "Приёмы_vet_id_fkey" FOREIGN KEY (vet_id) REFERENCES public."Сотрудники"(id) ON DELETE RESTRICT;
 S   ALTER TABLE ONLY public."Приёмы" DROP CONSTRAINT "Приёмы_vet_id_fkey";
       public               postgres    false    224    220    4675            L           2606    33490 8   Сотрудники Сотрудники_branch_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public."Сотрудники"
    ADD CONSTRAINT "Сотрудники_branch_id_fkey" FOREIGN KEY (branch_id) REFERENCES public."Филиалы"(id) ON DELETE RESTRICT;
 f   ALTER TABLE ONLY public."Сотрудники" DROP CONSTRAINT "Сотрудники_branch_id_fkey";
       public               postgres    false    218    4671    220            �   h   x�]���  ��R�`�Âl-���n�gk�������FV��c�p1T#�r�[���d ��Ҁ@�Z�>A5A����#�G(YP����d�+-��ι$@y      �   �   x�u�AN�0EדSxI����D���$	��ذ`��-D�RW�s#���
H�,˚?���A�����8`tW1�r��>�J�%��.��"x	~��H���#�/�c���E��$z��T�ܾe������:��	��@�G�ւ��(Ag�0������ٳ�����Q{�Xԇl�=[3tSJ{�	͌�/c[�3G�h�9:�gT���Y���%ę�a�eM����eQ?YDФ      �   ]  x�}�MN�0F��S�Hv��]�D"�X��e�v�U�B����4��Ҟa|#>O�6P��{��o<��s�8�o9���;�����1��pi'\FWM�&�r�_\�XiGR��1o퐴2��*��7��x��r�+\��m(0����k��`ܲt�s����q^kJ�;�v=�G���G�������Vv$/�w�@2��.���YBv�����=![!�:����{�Q'�o��8Nd�z��?t�3�þ�=�������v���F���_<_�AVXUk%{���� ��0
A?�b˅��k��]�s�;��Y$�K�e��ϒ�[ǆh(2�Ğ�8RJ}h��	      �   �   x�E�MN�@���)�մ���0I�`Q�"��@!���@H���o��LJ����󳗂gD�Z��>h�V���N�����,���!j���V�蘥�H�Q�k��+�Z�Fb�h�N�0 0Y���a�C����jƔ�O'6W��9R�;�6I���?�:2��-U���rg����r�p%xcGH����������l8b=��k�qk��-�Q��P|�FVۤ�]2�.7��!��Ո*g�͢(�?�1�      �   �   x�3估���{/6]l�����=@v�����/��S�����b���!���������!pq^XT���V�B�H���p�F@�e�ya:���@�U'�0�N�Vc �2�0�¾����d;�f	�v��&@����� ]���     
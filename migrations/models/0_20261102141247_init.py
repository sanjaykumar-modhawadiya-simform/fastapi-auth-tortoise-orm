from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "employees" (
    "user_id" SERIAL NOT NULL PRIMARY KEY,
    "user_name" VARCHAR(50) NOT NULL UNIQUE,
    "user_password" VARCHAR(255) NOT NULL,
    "role" VARCHAR(9) NOT NULL,
    "salary" DECIMAL(10,2) NOT NULL,
    "is_active" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_employees_user_na_57ff61" ON "employees" ("user_name");
COMMENT ON COLUMN "employees"."role" IS 'EMPLOYEE: employee\nDEVELOPER: developer\nHR: hr\nMANAGER: manager\nADMIN: admin';
COMMENT ON TABLE "employees" IS 'Employee database model representing system users and employees.';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztl19P2zAQwL9KlKdOYlXbAYO+pTQbndoGQcY2xhS5iWktHDvYDlAxvvtsJ2lapy1FAj"
    "YmnlrfH/vyO9t3vrNjGkHM626cYDqF0G5bdzYBsfpT0W1ZNkiSUqMEAoywNoa5lZaCERcM"
    "hEIqLgDmUIoiyEOGEoEoUebFpFYE5BSAQ0vPaTGYMMghEYiMLT7lAsZWyiHjFiCRNVukrl"
    "aJaCiXkYZPNWFK0FUKA0HHUEwgk9P+/CXFiETwVn5YPkwugwsEcbTACkVqAi0PxDTRsh4R"
    "n7ShinUUhBSnsf54tX6QeSRTMaFk5oKIUNIxJJABAdUagqWKH0kxzlkXSLNwS5MszjmfCF"
    "6AFKssKO8silJmB8HQ84MT1w8Cu5KhwmOOcS4KKVHZlaFyjWCsQnjfam5/3N77sLu9J010"
    "mDPJx/ts6ZJO5qgZDX37Xutl2jILDbokq2HpQQXwwQSwNYQLJ4OxDN5kXBD9dyHH4DbAkI"
    "zFRA53GmuInjrHB4fOcW2n8U4tSOU5zE7oMNe0tEpBNyAngPMbypbs5AdAzzs+DexCUNIu"
    "75EXx93a2dmAt7RaCVzrFokzilfsaJeksYbdkzEBEsIK9ML35VjPrnf7ccRtd3DU9364bn"
    "t21Z6Trnvq9r0j97htRfAaYppAdk4O5XAifwfO0PmsdDEgYKw0TnfQG7YtEMWImPf+Jvnb"
    "3yB7+ytzt29mjgMM2LSauy4MUQzw8nNSOhlJizKveu79XAls1BvPdFbWwO26B72B0681G1"
    "stzZdfYSTgPPftylWEeCA7B3S95HR0qNz4gCwnvOBnQB5Jx+ciW5SBl0Xb8by+mjnmkqkW"
    "9HxjB38ddNzjWtMAXxTcEnjIoEISALFkT0uNQDFcjnzR09zYuWu9+PMa64D8wMgjeJrneU"
    "1C/N7APfGdwdFCVrqO7ypNS0unhrS2a9w6s0msbz3/0FJD68wbuhov5WLM9IqlnX9mq5hA"
    "KmhA6E0AornOpJAW1O5V93pxOddlKcEIhJc3gEVBRUNbdJVtVRW3YlOi7+8oh6vCzB8UDm"
    "QonNhLnhq5Zu1DA5Q2D70yVuf5pTr9tyZ//s5Z3eRfyweZCukRneecy1vPuVnPqQ7VIwjn"
    "5v8h3WZjkxeUtFpJV+uMOkqJgGRJEf1y4g1XFNDSxayeKBTWbwsjXrkrXgHtNXAVjIUSWT"
    "CtDZzvJu6Dvtcxa5+aoCPR/9Vidv8H5ScnuA=="
)

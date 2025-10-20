import argparse
import getpass
import bcrypt


def main():
    parser = argparse.ArgumentParser(description="Generar hash bcrypt para usuarios")
    parser.add_argument("--password", "-p", help="Contraseña en texto plano. Si se omite, se pedirá por entrada segura.")
    parser.add_argument("--username", "-u", help="Nombre de usuario (opcional, para generar SQL INSERT)")
    parser.add_argument("--role", "-r", default="user", help="Rol del usuario (por defecto: user). Solo se usa al imprimir SQL INSERT si tu tabla lo tiene.")
    parser.add_argument("--sql", action="store_true", help="Imprimir sentencia SQL INSERT lista para MySQL (no ejecuta nada)")
    args = parser.parse_args()

    if args.password:
        pwd_plain = args.password
    else:
        pwd_plain = getpass.getpass("Ingresa la contraseña: ")
        confirm = getpass.getpass("Confirma la contraseña: ")
        if pwd_plain != confirm:
            raise SystemExit("Las contraseñas no coinciden.")

    hashed = bcrypt.hashpw(pwd_plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    print("Hash bcrypt generado:")
    print(hashed)

    if args.sql:
        if args.username:
            # Ajusta los campos según tu esquema real de la tabla `usuarios`
            # Ejemplos de esquemas soportados:
            # - (username, password_hash)
            # - (username, password_hash, role)
            print("\n-- SQL sugerido (ajústalo a tu esquema real):")
            print("-- Opción A: si tu tabla tiene columnas (username, password_hash)")
            print(f"INSERT INTO usuarios (username, password_hash) VALUES ('{args.username}', '{hashed}');")
            print("\n-- Opción B: si tu tabla tiene columnas (username, password_hash, role)")
            print(f"INSERT INTO usuarios (username, password_hash, role) VALUES ('{args.username}', '{hashed}', '{args.role}');")
        else:
            print("\nSugerencia: usa --username para imprimir la sentencia INSERT completa.")


if __name__ == "__main__":
    main()

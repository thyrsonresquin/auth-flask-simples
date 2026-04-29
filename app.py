import os
import bcrypt
from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
# view login <- rota para redirecionar usuários não autenticados
login_manager.login_view = 'login'

# session <- conexão ativa com o banco de dados
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)  # verifica se o usuário está autenticado
            return jsonify({'message': 'autenticação realizada com sucesso!!'}), 200
    return jsonify({'message': 'credenciais invalidas'}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'logout realizado com sucesso!!'}), 200

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    if username and password:
        user = User(username=username, password=hashed_password, role='user')
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'usuário criado com sucesso!!'}), 201
    return jsonify({'message': 'dados inválidos'}), 400

@app.route('/user/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'usuário não encontrado'}), 404
    if user.id != current_user.id:
        return jsonify({'message': 'acesso negado'}), 403
    return jsonify({'username': user.username})

@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)

    if user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'message': 'operação não permitida!'}), 403
    
    if user and data.get('password'):
        user.password = data.get('password')
        db.session.commit()
        return jsonify({'message': 'senha atualizada com sucesso!!'}), 200
    return jsonify({'message': 'dados inválidos'}), 400

@app.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if current_user.role != 'admin':
        return jsonify({'message': 'operação não permitida!'}), 403
    if not user:
        return jsonify({'message': 'usuário não encontrado'}), 404
    if user.id != current_user.id:
        return jsonify({'message': 'acesso negado'}), 403
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'usuário excluído com sucesso!!'}), 200

@app.route('/hello', methods=['GET'])
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
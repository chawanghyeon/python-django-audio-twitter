import { instance } from './index';

function signUp(data) {
	return instance.post('/signup', data);
}

function signIn(data) {
	return instance.post('/signin', data);
}

function updateUserInfo(data) {
	return instance.put(`user/${data.id}`, data);
}

export { signUp, signIn, updateUserInfo };

import { instance, mvcInstance } from './index';

function signUp(data) {
	return instance.post('/signup', data);
}

function signIn(data) {
	return instance.post('/login', data);
}

function allClient(data) {
	return instance.get('/getMemberList', data);
}

function updateUserInfo(data) {
	return mvcInstance.put(`user/${data.id}`, data);
}

export { signUp, signIn, allClient, updateUserInfo };

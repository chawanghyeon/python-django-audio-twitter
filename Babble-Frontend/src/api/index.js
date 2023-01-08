import { setInterceptors } from './interceptors';
import axios from 'axios';

function createInstance(url) {
	return axios.create({
		baseURL: url,
	});
}

// 엑시오스 초기화 함수
function createInstanceWithAuth(url) {
	const instance = axios.create({
		baseURL: url,
	});
	return setInterceptors(instance);
}

export const instance = createInstanceWithAuth('http://192.168.35.123:');

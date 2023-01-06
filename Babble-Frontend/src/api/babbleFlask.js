import { flaskInstance } from './index';

const config = { headers: { 'Content-Type': 'multipart/form-data' } };

function checkAudio(formData) {
	return flaskInstance.post('STT', formData, config);
}

export { checkAudio };

import { instance } from './index';

function insertBabble(babble) {
	return instance.post('babble', babble);
}

function deleteBabble(id) {
	return instance.delete(`/babble/${id}`);
}

function getBabble(id) {
	return instance.get(`/babble/${id}`);
}

function getBabbles() {
	return instance.get('babbles');
}

function getBabblesWithTag(id) {
	return instance.get(`tag/${id}`);
}

function insertRebabble(babble) {
	return instance.post('rebabble', babble);
}

function getUser(id) {
	return instance.get(`user/${id}`);
}

function insertComment(comment) {
	return instance.post(`comment`, comment);
}

function deleteComment(commentId) {
	return instance.delete(`comment/${commentId}`);
}

function like(id) {
	return instance.post(`like`);
}

function unlike(id) {
	return instance.delete(`like/${id}`);
}

function follow(id) {
	return instance.post(`follower`);
}

function unfollow(id) {
	return instance.delete(`follower/${id}`);
}

export {
	insertBabble,
	deleteBabble,
	getBabble,
	getBabbles,
	getBabblesWithTag,
	insertRebabble,
	getUser,
	insertComment,
	like,
	unlike,
	deleteComment,
	follow,
	unfollow,
};

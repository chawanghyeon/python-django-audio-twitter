import { elInstance } from './index';

const config = { headers: { 'Content-Type': 'application/json' } };

function sendNotification(query) {
	return elInstance.post(`notification/_doc`, query, config);
}

function getNotifications(id) {
	return elInstance.get(
		`notification/_search?q=receiver:${id}&sort=timestamp:desc`,
		config
	);
}

function sendCommentNotification(babble, user) {
	if (babble.user.id !== user.id) {
		const query = {
			sender: user.id,
			sender_avatar: user.avatar,
			receiver: babble.user.id,
			babble: babble.id,
			message: `${user.username}님이 회원님의 배블에 댓글을 달았습니다.`,
			timestamp: Date.now(),
		};
		sendNotification(query);
	}
}

function sendRebabbleNotification(babble, user) {
	if (babble.user.id !== user.id) {
		const query = {
			sender: user.id,
			sender_avatar: user.avatar,
			receiver: babble.user.id,
			babble: babble.id,
			message: `${user.username}님이 회원님의 배블을 리배블 했습니다.`,
			timestamp: Date.now(),
		};
		sendNotification(query);
	}
}

function sendLikeNotification(babble, user) {
	if (babble.user.id !== user.id) {
		console.log(user.id);
		const query = {
			sender: user.id,
			sender_avatar: user.avatar,
			receiver: babble.user.id,
			babble: babble.id,
			message: `${user.username}님이 회원님의 배블을 좋아합니다.`,
			timestamp: Date.now(),
		};
		sendNotification(query);
	}
}

function sendFollowNotification(profileUser, currentUser) {
	if (profileUser.id !== currentUser.id) {
		const query = {
			sender: currentUser.id,
			sender_avatar: currentUser.avatar,
			receiver: profileUser.id,
			message: `${currentUser.username}님이 회원님을 팔로우합니다.`,
			timestamp: Date.now(),
		};
		sendNotification(query);
	}
}

export {
	sendNotification,
	sendCommentNotification,
	sendRebabbleNotification,
	sendLikeNotification,
	sendFollowNotification,
	getNotifications,
};

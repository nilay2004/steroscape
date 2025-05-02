import { Users } from '../../../lib/database_ops/models';
// @ts-ignore
import { getRandomChar } from '$lib/globals';
import bcrypt from 'bcryptjs';
import { writeFileSync } from 'fs';
import { join } from 'path';
import sharp from 'sharp';
// @ts-ignore
import { PUBLIC_STATIC_PATH } from '$env/static/public';
const js = (obj:any) => JSON.stringify(obj)
export const saveImage: (avatar: File, output?: string) => Promise<string> = async (
	avatar,
	output = '/images/users'
) => {
	if (avatar && avatar.name !== undefined) {
		const file_name: string =
			getRandomChar(12, { numbers: false, lowercase: true }) + '.' + avatar.name.split('.').pop();
		const arrayBuffer = await avatar.arrayBuffer();
		const resizedImage = await sharp(arrayBuffer).resize({ width: 400 }).toBuffer();
		const filePath = join(output, file_name);
		writeFileSync(filePath, resizedImage);
		return file_name;
	}
	return '';
};
export const signIn: (form: FormData) => Promise<Response> = async (form) => {
	let user_ = form.get('username')
	let pass = form.get('password')
	const user = await Users.findOne({$or: [
		{username: user_},
		{email: user_}
	]})
	if(user === null)
		return new Response(js({success: 0, message: 'User is not exist with this email address!'}), {status: 200})
	if(bcrypt.compareSync(pass, user.password))
		return new Response(js({user: {id: user._id, fullname: user.fullname, username: user.username, avatar: user.avatar, passion: user.passion, email: user.email}, message: 'successfully logged!', success: 1}), {status: 200})
	else
		return new Response(js({message: 'Password is incorrect please supply correct password!', success: 0}), {status: 200})
};
export const signUp: (form: FormData) => Promise<Response> = async (form) => {
	let email = form.get('email');
	if (await Users.countDocuments({ email }))
		return new Response(
			JSON.stringify({
				message:
					'User with this email address is already exist please choose another email address!',
				success: 0
			}),
			{ status: 422 }
		);
	let profile = '';
	let avatar = form.get('avatar');
	if (avatar !== '') {
		profile = await saveImage(avatar as File, PUBLIC_STATIC_PATH + '/media/users');
		if (profile != '') profile = '/media/users/' + profile;
	}
	let user = await Users({
		fullname: form.get('fullname'),
		username: form.get('username'),
		email: form.get('email'),
		passion: form.get('passion'),
		password: bcrypt.hashSync(form.get('password')),
		avatar: profile
	});
	try {
		await user.save();
		return new Response(
			JSON.stringify({
				user: {
					id: user._id,
					email: user.email,
					fullname: user.fullname,
					passion: user.passion,
					username: user.username,
					avatar: user.avatar
				},
				success: 1,
				message: 'Successfully saved!'
			})
		);
	} catch (err) {
		return new Response(JSON.stringify({ success: 0, message: err.message }), { status: 422 });
	}
};

export const checkUser = async (u: string) =>
	new Response(JSON.stringify({ user: await Users.countDocuments({ username: u }) }), {
		status: 200
	});

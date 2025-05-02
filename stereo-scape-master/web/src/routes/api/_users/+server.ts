// @ts-ignore
import database from '$lib/database_ops/database';
// @ts-ignore
import { checkUser, signIn, signUp } from './users_ops';

await database.connect();
export const POST = async ({ request }: any) => {
	const req = request.headers.get('request');
	if (req === 'sign_up') return signUp(await request.formData());
	if (req === 'signIn') return signIn(await request.formData());
	return new Response(
		JSON.stringify({ message: "Don't try to access api without authorization!" }),
		{ status: 401 }
	);
};
export const GET = async ({ url }: any) => {
	if (url.searchParams.get('username')) {
		return await checkUser(url.searchParams.get('username'));
	}
	return new Response(JSON.stringify({ message: 'API working fine' }));
};

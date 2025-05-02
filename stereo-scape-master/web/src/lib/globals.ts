const PUBLIC_ENV = 'dev';
export const parse = (json: {} | []) => {
	if (json) return JSON.parse(JSON.stringify(json));
	else return json;
};
export const lazyLoad = (element: HTMLImageElement | HTMLVideoElement, src: any) => {
  const loaded = () => {
    element.style.opacity = "1";
  };
  const observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting) {
        element.src = src;
        if ((element as any).complete) {
          loaded();
        } else {
          element.addEventListener("load", loaded);
        }
      }
    },
    {
      root: null,
      rootMargin: "0px",
      threshold: 0,
    }
  );
  observer.observe(element);
  return {
    destroy() {
      element.removeEventListener("load", loaded);
    },
  };
};
export const createForm: (elements:{[key:string]: any}) => FormData = (elements) => {
	const form = new FormData()
	for(let item of Object.keys(elements))
		form.append(item, elements[item])
	return form 
}
export const life = (__time__: string) => {
	/**
	 * Format Datetime (Created by LittleZabi -> blueterminal Lab )
	 * @param {time} time object
	 * FORMATS:
	 * month formats ~
	 * MM -> full month name e.g March
	 * Mm -> short month name e.g Mar
	 * mm -> month number with zero if month < 10 e.g 03
	 * m -> month number e.g 3
	 * Date formats ~
	 * Do -> Date with ordinal indicators like 1st, 2nd, 3rd, 20th
	 * DD -> Date with zero if Date less then 10 e.g 08
	 * D -> only Date number
	 * Days formats ~
	 * dddd -> Day of the week full like Monday
	 * ddd -> Day of the week only 3 chars like Mon
	 * dd -> Day of the week only 2 chars like Mo
	 * Year formats ~
	 * YYYY -> Full Year like 2023
	 * YY -> only last two numbers like 23
	 */
	let dt = new Date(__time__);
	if (!dt.getDate()) dt = new Date();
	const mF = (_i: number) =>
		'January_February_March_April_May_June_July_August_September_October_November_December'.split(
			'_'
		)[_i];
	const mS = (_i: number) => 'Jan_Feb_Mar_Apr_May_Jun_Jul_Aug_Sep_Oct_Nov_Dec'.split('_')[_i];
	const dF = (_i: number) =>
		'Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday'.split('_')[_i];
	const dS = (_i: number) => 'Sun_Mon_Tue_Wed_Thu_Fri_Sat'.split('_')[_i];
	const dSx = (_i: number) => 'Su_Mo_Tu_We_Th_Fr_Sa'.split('_')[_i];
	const xd = [dt.getFullYear(), dt.getMonth(), dt.getDate(), dt.getDay()];
	return {
		format: (f_: string) => {
			let __: string = f_;
			if (f_.includes('MM')) __ = __.replace('MM', mF(xd[1]));
			if (f_.includes('Mm')) __ = __.replace('Mm', mS(xd[1]));
			if (f_.includes('mm'))
				__ = __.replace(
					'mm',
					xd[1] + 1 < 10 ? '0' + (xd[1] + 1).toString() : (xd[1] + 1).toString()
				);
			if (f_.includes('m')) __ = __.replace('m', (xd[1] + 1).toString());
			if (f_.includes('Do'))
				__ = __.replace(
					'Do',
					xd[2] > 3 ? xd[2].toString() + 'th' : xd[2] === 1 ? '1st' : xd[2] === 2 ? '2nd' : '3rd'
				);
			if (f_.includes('DD'))
				__ = __.replace('DD', xd[2] < 10 ? '0' + xd[1].toString() : xd[1].toString());
			if (f_.includes('D')) __ = __.replace('D', xd[2].toString());
			if (f_.includes('dddd')) __ = __.replace('dddd', dF(xd[3]).toString());
			if (f_.includes('ddd')) __ = __.replace('ddd', dS(xd[3]).toString());
			if (f_.includes('dd')) __ = __.replace('dd', dSx(xd[3]).toString());
			if (f_.includes('YYYY')) __ = __.replace('YYYY', xd[0].toString());
			if (f_.includes('YY')) __ = __.replace('YY', xd[0].toString().substring(2, 4));
			return __;
		},
		from: () => {
			let dn = new Date().getTime();
			let e = dn - dt.getTime();
			if (e < 1000) return 'Just now';
			const s = Math.floor(e / 1000);
			if (s < 60) return `${s} seconds ago`;
			const m = Math.floor(e / (60 * 1000));
			if (m < 60) return `${m} minutes ago`;
			const h = Math.floor(e / (1000 * 60 * 60));
			if (h < 24) return `${h} hours ago`;
			const d = Math.floor(e / (1000 * 60 * 60 * 24));
			if (d < 7) return d === 1 ? `24 hours ago` : `${d} days ago`;
			if (d <= 30) return `${Math.floor(d / 7)} week ago`;
			const mo = Math.floor(d / 30);
			if (mo >= 1 && mo < 12) return mo > 1 ? `${mo} months ago` : `1 month ago`;
			if (mo === 12) return '1 year ago';
			const moy = Math.floor((e % (1000 * 60 * 60 * 24 * 365)) / (1000 * 60 * 60 * 24 * 30));
			const y = Math.floor(e / (1000 * 60 * 60 * 24 * 365));
			if (moy === 0) return `${y} yrs ago`;
			return `${y} ${y === 1 ? 'years' : 'years'} and ${moy} months ago`;
		},
		dayPortion: () => {
			let a = '';
			let b = '';
			let curTime = dt.getHours();
			a =
				curTime >= 2 && curTime < 12
					? 'morning'
					: curTime >= 12 && curTime <= 18
						? 'afternoon'
						: 'evening';
			a = `Good ${a}!`;
			b =
				curTime >= 0 && curTime < 1
					? 'Midnight'
					: curTime >= 1 && curTime < 2
						? 'Middle of the night'
						: curTime >= 2 && curTime < 6
							? 'Early morning'
							: curTime >= 6 && curTime < 8
								? 'Dawn'
								: curTime >= 8 && curTime < 9
									? 'Morning'
									: curTime >= 9 && curTime < 12
										? 'Late morning'
										: curTime >= 12 && curTime < 13
											? 'Noon'
											: curTime >= 13 && curTime < 14
												? 'Afternoon'
												: curTime >= 14 && curTime < 17
													? 'Late afternoon'
													: curTime >= 17 && curTime < 18
														? 'Dusk'
														: curTime >= 18 && curTime < 19
															? 'Early evening'
															: curTime >= 19 && curTime < 21
																? 'Evening'
																: curTime >= 21 && curTime < 23
																	? 'Late evening'
																	: 'Night';
			return [a, b];
		}
	};
};
export const trimTitle = (title: string, minchars = 20, lastchars = 7, midchars = '...') => {
	const _len = title.length;
	if (_len < minchars) return title;
	let _ = '';
	if (_len > minchars + lastchars) {
		_ = title.substring(0, minchars);
		_ = _ + midchars + title.substring(_len - lastchars, _len);
	} else _ = title;
	return _;
};
export const setUserCharName = (name: string) => {
	const k = name.split(' ');
	let n = '';
	k.map((e, i) => (e ? (i < 2 ? (n += e[0]) : '') : ''));
	if (n === '') n = name[0];
	return n.toUpperCase();
};
export const numberFormat = (__num__: number): string => {
	if (typeof __num__ === 'number')
		return __num__ >= 1000000
			? (__num__ / 1000000).toFixed(1) + 'M'
			: __num__ >= 1000
				? (__num__ / 1000).toFixed(1) + 'k'
				: __num__.toString();
	else return '0';
};

export const staticBody = (visibility: Boolean) => {
	if (document) {
		if (visibility) document.querySelector('body')?.classList.add('modal-open');
		else document.querySelector('body')?.classList.remove('modal-open');
	}
};
/**
 * The set function of Cookies object can set cookies by using document.cookie
 * and you can set 
 * @param {typeof name} name of the cookie
 * @param {string | object} value to store
 * @param {typeof options} options where expires, maxAge, path, domain, secure, sameSite and other options is available
 * @param {typeof options.expires} options.expires you can set number of days
 * @param {typeof options.maxAge} options.maxAge is alternative solution of setting expires you can set in number of seconds.
 * @param {typeof options.path} options.path is path of available cookies the default is `/` its mean cookies will available for all pages and if `/login` is set then cookies will available only in login page.
 * */
export const Cookies: {
	set: (
		name: string,
		value: string | object,
		options?: {
			expires?: number | Date;
			maxAge?: number;
			path?: string;
			domain?: string;
			secure?: boolean;
			sameSite?: string;
		}
	) => void,
	get: (name: string) => string | null,
	delete: (name: string) => void
} = {
	set: (name, value, options) => {
		
		if (typeof value === 'object') value = JSON.stringify(value)
		options = options ? options : {};
		if (options?.expires) options.expires = new Date(Date.now() + 86400000 * Number(options.expires));
		options.path = options.path ? options.path : '/';
		options.secure = options.secure ? options.secure : PUBLIC_ENV === 'dev' ? false : true;
		let cookies = `${name}=${value}`;
		for (const option in options) {
			if (options.hasOwnProperty(option)) {
				if (option === 'maxAge') cookies += `;max-age=${options[option]}`;
				// @ts-ignore
				else cookies += `;${option}=${options[option]}`;
			}
		}
		document.cookie = cookies;
	},
	get: (name) => {
		let cookies = document.cookie.split(';');
		let value = null;
		for (const c of cookies) {
			let [n, v] = c.split('=');
			if (n.trim() === name) return decodeURIComponent(v);
		}
		return value;
	},
	delete: (name) => {
		document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
	}
}
const rand_options = {
	numbers: true,
	symbols: false,
	separator: false,
	segment: 5,
	uppercase: false,
	lowercase: false
};
export const getRandomChar = (
	length: number,
	options: {
		numbers?: boolean;
		symbols?: boolean;
		separator?: boolean | string;
		segment?: number;
		uppercase?: boolean;
		lowercase?: boolean;
	} = rand_options
) => {
	options = { ...rand_options, ...options };
	let nchar: string = '';
	let chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
	if (options.numbers) chars += '1234567890';
	if (options.symbols) chars += '!~#@$%^&*()_+={}[])|:;?.]';
	for (let i = 0; i < length; i++) {
		let r = Math.ceil(Math.random() * (chars.length - 2));
		if (options.separator && options.segment)
			if (i % options.segment === 0 && i !== 0 && i < length) nchar += options.separator;
		if (nchar === '') r = Math.ceil(Math.random() * (chars.length - 1));
		nchar += chars[r];
	}
	nchar = nchar.replace(/undefined/g, 'zabi');
	return options.uppercase ? nchar.toUpperCase() : options.lowercase ? nchar.toLowerCase() : nchar;
};

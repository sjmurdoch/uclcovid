use std::error::Error;
use std::io::BufReader;
use std::path::PathBuf;
use scraper::{Html, Selector};
use std::fs::{File};
use std::io::{Read};
use lazy_static::lazy_static;
use rayon::prelude::*;

lazy_static! {
    static ref SELECTOR: Selector = Selector::parse("#current-confirmed-cases-covid-19 > div.site-content.wrapper \
        > div > div > div > article > div > table th,td").unwrap();
}

fn show(last: &[String]) {
    for v in last {
        print!("{}, ", v);
    }
    println!();
}



fn parse_chunk(filenames: &[PathBuf]) -> Result<(), std::io::Error> {

    let mut last: [String; 23] = Default::default();
    let selector = Selector::parse("#current-confirmed-cases-covid-19 > div.site-content.wrapper \
    > div > div > div > article > div > table th,td").unwrap();

    for path in filenames {
        println!("Reading {}", path.display());

        let input = File::open(&path)?;
        let mut buffered = BufReader::new(input);
        let mut html = String::new();
        buffered.read_to_string(&mut html).unwrap();
        let html = Html::parse_document(&html);

        //let selector2 = Selector::parse("th,td").unwrap();

        let mut changed = false;
        for (i, element) in html.select(&selector).enumerate() {
            let text = element.text()
                .collect::<Vec<&str>>()
                .join(" ");
            if last[i] != text {
                last[i] = text;
                changed = true;
            }
            //println!("{}", element.inner_html());
        }
        if changed {
            show(&last);
        } else {
            println!("unchanged: {}", path.display())
        }

        //let soup = Soup::from_reader(buffered)?;
        //let h1 = soup.class("box").class("box").find().expect("Could not find node box");
        //let h2 = h1.tag("h2").find().expect("Could not find node h2");
        //println!("{}", h2.display());
        //header = soup.select_one('.box > h2:nth-child(1)')
        //table = soup.select_one('#current-confirmed-cases-covid-19 > div.site-content.wrapper > div > div > div > article > div > table')
    }

    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> {
    let filenames: Result<Vec<_>, _> = glob::glob("../../../data/original/covid-*.html")?.collect();

    let mut out = Vec::new(); 
    filenames?.par_chunks(10).map(parse_chunk).collect_into_vec(&mut out);

    //parse_chunk(&filenames)?;

    Ok(())
}
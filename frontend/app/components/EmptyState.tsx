import { MouseEvent } from "react";
import {
  Heading,
  Link,
  Card,
  CardHeader,
  Flex,
  Spacer,
} from "@chakra-ui/react";

export function EmptyState(props: { onChoice: (question: string) => any }) {
  const handleClick = (e: MouseEvent) => {
    props.onChoice((e.target as HTMLDivElement).innerText);
  };
  return (
    <div className="rounded flex flex-col items-center max-w-full md:p-8">
      <Flex marginTop={"25px"} grow={1} maxWidth={"800px"} width={"100%"}>
        <Card
          onMouseUp={handleClick}
          width={"48%"}
          backgroundColor={"rgb(58, 58, 61)"}
          _hover={{ backgroundColor: "rgb(78,78,81)" }}
          cursor={"pointer"}
          justifyContent={"center"}
        >
          <CardHeader justifyContent={"center"}>
            <Heading
              fontSize="lg"
              fontWeight={"medium"}
              mb={1}
              color={"gray.200"}
              textAlign={"center"}
            >
              列表（list）和元组（tuple）有什么区别？
            </Heading>
          </CardHeader>
        </Card>
        <Spacer />
        <Card
          onMouseUp={handleClick}
          width={"48%"}
          backgroundColor={"rgb(58, 58, 61)"}
          _hover={{ backgroundColor: "rgb(78,78,81)" }}
          cursor={"pointer"}
          justifyContent={"center"}
        >
          <CardHeader justifyContent={"center"}>
            <Heading
              fontSize="lg"
              fontWeight={"medium"}
              mb={1}
              color={"gray.200"}
              textAlign={"center"}
            >
              如何创建和使用虚拟环境？
            </Heading>
          </CardHeader>
        </Card>
      </Flex>
      <Flex marginTop={"25px"} grow={1} maxWidth={"800px"} width={"100%"}>
        <Card
          onMouseUp={handleClick}
          width={"48%"}
          backgroundColor={"rgb(58, 58, 61)"}
          _hover={{ backgroundColor: "rgb(78,78,81)" }}
          cursor={"pointer"}
          justifyContent={"center"}
        >
          <CardHeader justifyContent={"center"}>
            <Heading
              fontSize="lg"
              fontWeight={"medium"}
              mb={1}
              color={"gray.200"}
              textAlign={"center"}
            >
              如何用Python进行Web开发？有哪些常用的Web框架？
            </Heading>
          </CardHeader>
        </Card>
        <Spacer />
        <Card
          onMouseUp={handleClick}
          width={"48%"}
          backgroundColor={"rgb(58, 58, 61)"}
          _hover={{ backgroundColor: "rgb(78,78,81)" }}
          cursor={"pointer"}
          justifyContent={"center"}
        >
          <CardHeader justifyContent={"center"}>
            <Heading
              fontSize="lg"
              fontWeight={"medium"}
              mb={1}
              color={"gray.200"}
              textAlign={"center"}
            >
              如何优化Python代码的性能？
            </Heading>
          </CardHeader>
        </Card>
      </Flex>
    </div>
  );
}
